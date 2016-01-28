(function () {
    'use strict';

    angular
        .module('mturk.hit.controllers', [])
        .controller('HITController', HITController);

    HITController.$inject = ['$scope', '$location', '$mdToast', 'HIT', '$filter', '$sce'];

    function HITController($scope, $location, $mdToast, HIT, $filter, $sce) {
        var self = this;
        self.isAccepted = false;
        self.submit = submit;
        self.currentStatus = null;
        self.pk = null;
        self.MTURK_HOST = 'https://workersandbox.mturk.com/mturk/externalSubmit';
        self.getHost = getHost;
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
        function  getHost(){
            return $sce.trustAsResourceUrl(self.MTURK_HOST);
        }
    }
})
();


