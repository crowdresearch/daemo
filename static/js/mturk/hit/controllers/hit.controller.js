(function () {
    'use strict';

    angular
        .module('mturk.hit.controllers', [])
        .controller('HITController', HITController);

    HITController.$inject = ['$scope', '$state', '$mdToast', 'HIT', '$filter', '$sce', '$websocket', '$rootScope', '$stateParams'];

    function HITController($scope, $state, $mdToast, HIT, $filter, $sce, $websocket, $rootScope, $stateParams) {
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
            var hitId = $stateParams.hitId;
            var assignmentId = $stateParams.assignmentId;
            self.assignmentId = assignmentId;
            var workerId = $stateParams.workerId;
            var taskId = $stateParams.taskId;

            HIT.get_or_create(taskId, hitId, assignmentId, workerId).then(
                function success(response) {
                    self.taskData = response[0].task;
                    self.pk = response[0].assignment;
                    self.isAccepted = assignmentId !== 'ASSIGNMENT_ID_NOT_AVAILABLE';
                    if (self.isAccepted) {
                        initializeWebSocket();
                    }
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
                worker_id: $stateParams.workerId,
                assignment_id: $stateParams.assignmentId,
                hit_id: $stateParams.hitId
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
            if (self.isAccepted) {
                return $filter('filter')(self.taskData.template.template_items, {role: 'input'}).length > 0;
            }
            return false;
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
                    console.log('opened');
                })
                .$open();
        }

        function receiveMessage(data) {
            if (!self.taskData) {
                return;
            }
            var message = JSON.parse(data);
            if ($location.search().taskId != message.task_id) return;
            var inputItems = $filter('filter')(self.taskData.template.template_items, {role: 'input'});
            var remoteContentItems = $filter('filter')(self.taskData.template.template_items, {type: 'iframe'});
            var item = $filter('filter')(self.taskData.template.template_items, {id: message.template_item});
            if (inputItems.length == 0 && item.length && item[0].aux_attributes.src.indexOf(message.daemo_id) > 0) {
                item[0].isSubmitted = true;
                var submitted = $filter('filter')(self.taskData.template.template_items, {
                    isSubmitted: true,
                    type: 'iframe'
                });
                if (remoteContentItems.length == submitted.length) {
                    self.submit();
                }
            }
            $scope.$apply();
        }
    }
})
();


