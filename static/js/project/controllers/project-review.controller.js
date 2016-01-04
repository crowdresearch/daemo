(function () {
    'use strict';

    angular
        .module('crowdsource.project.controllers')
        .controller('ProjectReviewController', ProjectReviewController);

    ProjectReviewController.$inject = ['$scope', 'Project', 'resolvedData', '$routeParams', 'Task', '$mdToast',
        '$filter'];

    /**
     * @namespace ProjectReviewController
     */
    function ProjectReviewController($scope, Project, resolvedData, $routeParams, Task, $mdToast, $filter) {
        var self = this;
        self.tasks = [];
        self.loading = true;
        self.loadingSubmissions = true;
        self.submissions = [];
        self.resolvedData = {};
        self.getQuestionNumber = getQuestionNumber;
        self.hasOptions = hasOptions;
        self.listSubmissions = listSubmissions;
        self.isSelected = isSelected;
        self.selectedTaskId = null;
        self.taskData = null;
        self.selectedTask = null;
        self.toggleSelected = toggleSelected;
        self.getResult = getResult;
        self.acceptAll = acceptAll;
        self.showAcceptAll = showAcceptAll;
        self.getStatus = getStatus;
        self.updateStatus = updateStatus;
        self.downloadResults = downloadResults;
        self.status = {
            RETURNED: 5,
            REJECTED: 4,
            ACCEPTED: 3,
            SUBMITTED: 2
        };
        activate();
        function activate() {
            self.resolvedData = resolvedData[0];
            Task.getTasks(self.resolvedData.id).then(
                function success(response) {
                    self.loading = false;
                    self.tasks = response[0];
                },
                function error(response) {
                    $mdToast.showSimple('Could not get tasks.');
                }
            ).finally(function () {
            });
        }

        function listSubmissions(task) {
            Task.retrieve(task.id).then(
                function success(response) {
                    self.taskData = response[0];
                },
                function error(response) {
                    $mdToast.showSimple('Could not get submissions.');
                }
            ).finally(function () {
            });
            Task.listSubmissions(task.id).then(
                function success(response) {
                    self.submissions = response[0];
                    self.selectedTask = task;
                    self.loadingSubmissions = false;
                },
                function error(response) {
                    $mdToast.showSimple('Could not get submissions.');
                }
            ).finally(function () {
            });
        }

        function getQuestionNumber(resultObj) {
            var item = $filter('filter')(self.resolvedData.templates[0].template_items,
                {id: resultObj.template_item})[0];
            return item.position;
        }

        function hasOptions(item) {
            return item.aux_attributes.hasOwnProperty('options');
        }

        function isSelected(task) {
            return angular.equals(task, self.selectedTask);
        }

        function toggleSelected(item) {
            if (angular.equals(item, self.selectedTask)) {
                self.selectedTask = null;
                self.submissions = [];
                self.taskData = null;
                self.loadingSubmissions = true;
            }
            else {
                self.listSubmissions(item);
            }
        }

        function getResult(result) {
            if (Object.prototype.toString.call(result) === '[object Array]') {
                return $filter('filter')(result, {answer: true}).map(function (obj) {
                    return obj.value;
                }).join(', ');
            }
            else {
                return result;
            }
        }

        function acceptAll() {
            Task.acceptAll(self.selectedTask.id).then(
                function success(response) {
                    var submissionIds = response[0];
                    angular.forEach(submissionIds, function (submissionId) {
                        var submission = $filter('filter')(self.submissions, {id: submissionId})[0];
                        submission.task_status = self.status.ACCEPTED;
                    });
                },
                function error(response) {
                    $mdToast.showSimple('Could accept submissions.');
                }
            ).finally(function () {
            });
        }

        function showAcceptAll() {
            return $filter('filter')(self.submissions, {task_status: self.status.SUBMITTED}).length;
        }

        function getStatus(statusId) {
            for (var key in self.status) {
                if (self.status.hasOwnProperty(key)) {
                    if (statusId == self.status[key])
                        return key;
                }

            }
        }

        function updateStatus(status, taskWorker) {
            var request_data = {
                "task_status": status,
                "task_workers": [taskWorker.id]
            };
            Task.updateStatus(request_data).then(
                function success(response) {
                    taskWorker.task_status = status;
                },
                function error(response) {
                    $mdToast.showSimple('Could return submission.');
                }
            ).finally(function () {
            });
        }

        function downloadResults() {
            var params = {
                project_id: self.resolvedData.id
            };
            Task.downloadResults(params).then(
                function success(response) {
                    var a = document.createElement('a');
                    a.href = 'data:text/csv;charset=utf-8,' + response[0].replace(/\n/g, '%0A');
                    a.target = '_blank';
                    a.download = self.resolvedData.name.replace(/\s/g, '') + '_data.csv';
                    document.body.appendChild(a);
                    a.click();
                },
                function error(response) {

                }
            ).finally(function () {
            });
        }
    }
})();
