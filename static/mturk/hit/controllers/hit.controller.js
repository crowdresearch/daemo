(function () {
    'use strict';

    angular
        .module('mturk.hit.controllers', [])
        .controller('HITController', HITController);

    HITController.$inject = ['$scope', '$location', '$mdToast', 'HIT', '$filter', '$sce', '$websocket'];

    function HITController($scope, $location, $mdToast, HIT, $filter, $sce, $websocket) {
        var self = this;
        self.isAccepted = false;
        self.submit = submit;
        self.currentStatus = null;
        self.pk = null;
        self.MTURK_HOST = 'https://workersandbox.mturk.com/mturk/externalSubmit';
        self.getHost = getHost;
        self.showSubmit = showSubmit;
        activate();
        function activate() {
            var hitId = $location.search().hitId;
            var assignmentId = $location.search().assignmentId;
            self.assignmentId = assignmentId;
            var workerId = $location.search().workerId;
            var taskId = $location.search().taskId;
            HIT.get_or_create(taskId, hitId, assignmentId, workerId).then(
                function success(response) {
                    self.taskData = response[0].task;
                    self.pk = response[0].assignment;
                    self.isAccepted = assignmentId !== 'ASSIGNMENT_ID_NOT_AVAILABLE';
                },
                function error(response) {
                    $mdToast.showSimple('Could not get task data.');
                }
            ).finally(function () {
            });

            HIT.get_url().then(
                function success(response) {
                    self.MTURK_HOST = response[0].url;
                },
                function error(response) {
                    $mdToast.showSimple('Could not get worker host.');
                }
            ).finally(function () {
                initializeWebSocket();
            });
        }

        function submit() {
            var itemsToSubmit = $filter('filter')(self.taskData.template.template_items, {role: 'input'});
            var itemAnswers = [];
            var missing = false;
            self.status = {
                RETURNED: 5,
                REJECTED: 4,
                ACCEPTED: 3,
                SUBMITTED: 2,
                CREATED: 1
            };
            angular.forEach(itemsToSubmit, function (obj) {
                if ((!obj.answer || obj.answer == "") && obj.type != 'checkbox') {
                    missing = true;
                }

                if (obj.type != 'checkbox') {
                    itemAnswers.push(
                        {
                            template_item: obj.id,
                            result: obj.answer || ""
                        }
                    );
                }
                else {
                    itemAnswers.push(
                        {
                            template_item: obj.id,
                            result: obj.aux_attributes.options
                        }
                    );
                }
            });
            if (missing) {
                $mdToast.showSimple('All fields are required.');
                return;
            }
            var requestData = {
                task: self.taskData.id,
                template_items: itemAnswers,
                worker_id: $location.search().workerId,
                assignment_id: $location.search().assignmentId,
                hit_id: $location.search().hitId
            };
            HIT.submit_results(self.pk, requestData).then(
                function success(data, status) {
                    self.currentStatus = true;
                    $('#mturkForm').submit();
                },
                function error(data, status) {
                    $mdToast.showSimple('Could not submit task!');

                }).finally(function () {
                }
            );
        }

        function getHost() {
            return $sce.trustAsResourceUrl(self.MTURK_HOST);
        }

        function showSubmit() {
            return $filter('filter')(self.taskData.template.template_items, {role: 'input'}).length > 0 && self.isAccepted;
        }

        function initializeWebSocket() {
            self.ws = $websocket.$new({
                url: $rootScope.getWebsocketUrl() + '/ws/external?subscribe-broadcast',
                lazy: true,
                reconnect: true
            });
            self.ws
                .$on('$message', function (data) {
                    receiveMessage(data);
                })
                .$on('$close', function () {

                })
                .$on('$open', function () {

                })
                .$open();
        }

        function receiveMessage(data) {
            console.log(self.taskData);
            if (!self.taskData){
                return;
            }
            var message = JSON.parse(data);
            if ($location.search().taskId != message.task_id) return;
            var inputItems = $filter('filter')(self.taskData.template.template_items, {role: 'input'});
            var remoteContentItems = $filter('filter')(self.taskData.template.template_items, {type: 'iframe'});
            if(inputItems.length == 0){
                var item = $filter('filter')(self.taskData.template.template_items, {id: message.template_item});
                item[0].isSubmitted = true;
                var submitted = $filter('filter')(self.taskData.template.template_items, {isSubmitted: true, type: 'iframe'});
                if(remoteContentItems.length == submitted.length) {
                    self.submit();
                }
            }
            $scope.$apply();
        }
    }
})
();


