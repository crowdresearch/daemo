(function () {
    'use strict';

    angular
        .module('crowdsource.project.controllers')
        .controller('ProjectReviewController', ProjectReviewController);

    ProjectReviewController.$inject = ['$scope', 'Project', 'resolvedData', '$stateParams', 'Task', '$mdToast',
        '$filter', 'RatingService', '$mdDialog', '$state'];

    /**
     * @namespace ProjectReviewController
     */
    function ProjectReviewController($scope, Project, resolvedData, $stateParams, Task, $mdToast,
                                     $filter, RatingService, $mdDialog, $state) {
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
        self.setSelected = setSelected;
        self.getQuestion = getQuestion;
        self.getResult = getResult;
        self.acceptAll = acceptAll;
        self.showAcceptAll = showAcceptAll;
        self.getStatus = getStatus;
        self.updateStatus = updateStatus;
        self.downloadResults = downloadResults;
        self.setRating = setRating;
        self.showActions = showActions;
        self.returnTask = returnTask;
        self.revisionChanged = revisionChanged;
        self.getOtherResponses = getOtherResponses;
        self.getRated = getRated;
        self.goToRating = goToRating;
        self.selectedRevision = null;
        self.lastOpened = null;
        self.status = {
            RETURNED: 5,
            REJECTED: 4,
            ACCEPTED: 3,
            SUBMITTED: 2
        };
        activate();
        function activate() {
            self.resolvedData = resolvedData[0];
            self.selectedRevision = self.resolvedData.id;
            self.revisions = self.resolvedData.revisions;
            Project.getWorkersToRate(self.resolvedData.id).then(
                function success(response) {
                    self.loading = false;
                    self.workers = response[0].workers;
                    retrieveLastOpened();
                    getRated();
                },
                function error(response) {
                    $mdToast.showSimple('Could not fetch workers to rate.');
                }
            ).finally(function () {
            });
        }


        function retrieveLastOpened() {
            Project.lastOpened(self.resolvedData.id).then(
                function success(response) {
                    self.lastOpened = response[0].last_opened_at;
                },
                function error(response) {

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

        function getQuestionNumber(list, item) {
            // get position if item is input type
            var position = '';

            if (item.role == 'input') {
                var inputItems = $filter('filter')(list,
                    {role: 'input'});

                position = _.findIndex(inputItems, function (inputItem) {
                        return inputItem.id == item.id;
                    }) + 1;
                position += ') ';
            }

            return position;
        }

        function hasOptions(item) {
            return item.aux_attributes.hasOwnProperty('options');
        }

        function isSelected(task) {
            return angular.equals(task, self.selectedTask);
        }

        function setSelected(item) {
            if (angular.equals(item, self.selectedTask)) {
                return null;
            }
            else {
                self.listSubmissions(item);
            }
        }

        function getQuestion(list, item) {
            return getQuestionNumber(list, item) + item.aux_attributes.question.value
        }

        function getResult(result) {
            var item = $filter('filter')(self.resolvedData.template.items,
                {id: result.template_item})[0];

            if (Object.prototype.toString.call(result.result) === '[object Array]') {
                return $filter('filter')(result.result, {answer: true}).map(function (obj) {
                    return obj.value;
                }).join(', ');
            }
            else if (item.type == 'iframe') {
                var resultSet = [];
                angular.forEach(result.result, function (value, key) {
                    resultSet.push(key + ': ' + value);
                });
                resultSet = resultSet.join(', ');

                return getQuestionNumber(self.resolvedData.template.items, item) + resultSet;
            }
            else {
                return getQuestionNumber(self.resolvedData.template.items, item) + result.result;
            }
        }

        function acceptAll() {
            Task.acceptAll(self.selectedTask.id).then(
                function success(response) {
                    var submissionIds = response[0];
                    angular.forEach(submissionIds, function (submissionId) {
                        var submission = $filter('filter')(self.submissions, {id: submissionId})[0];
                        submission.status = self.status.ACCEPTED;
                    });
                },
                function error(response) {
                    $mdToast.showSimple('Could accept submissions.');
                }
            ).finally(function () {
            });
        }

        function showAcceptAll() {
            return $filter('filter')(self.submissions, {status: self.status.SUBMITTED}).length;
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
                "status": status,
                "workers": [taskWorker.id]
            };
            Task.updateStatus(request_data).then(
                function success(response) {
                    taskWorker.status = status;
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

        function showActions(workerAlias) {
            return workerAlias.indexOf('mturk') < 0;
        }

        function goToRating() {
            $state.go('project_rating', {projectId: self.resolvedData.id});
        }

        function returnTask(taskWorker, status, worker_alias, e) {
            if (!self.feedback) {
                self.current_taskWorker = taskWorker;
                self.current_taskWorker.worker_alias = worker_alias;
                showReturnDialog(e);
            } else {
                var request_data = {
                    "task_worker": self.current_taskWorker.id,
                    "body": self.feedback
                };
                Task.submitReturnFeedback(request_data).then(
                    function success(response) {
                        updateStatus(self.status.RETURNED, self.current_taskWorker);
                        self.feedback = null;
                        self.current_taskWorker.status = self.status.RETURNED;
                    },
                    function error(response) {
                        $mdToast.showSimple('Could not return submission.');
                    }
                ).finally(function () {
                });
            }
        }

        function showReturnDialog($event) {
            var parent = angular.element(document.body);
            $mdDialog.show({
                clickOutsideToClose: true,
                scope: $scope,
                preserveScope: true,
                parent: parent,
                targetEvent: $event,
                templateUrl: '/static/templates/project/return.html',
                locals: {
                    taskWorker: self.current_taskWorker
                },
                controller: DialogController
            });
        }

        function DialogController($scope, $mdDialog) {
            $scope.hide = function () {
                $mdDialog.hide();
            };
            $scope.cancel = function () {
                $mdDialog.cancel();
            };
        }

        function revisionChanged() {
            if (self.selectedRevision != self.resolvedData.id) {
                $state.go('project_review', {projectId: self.selectedRevision});
            }
        }

        function getRated() {
            self.ratedWorkers = 0;
            for (var i = 0; i < self.workers.length; i++) {
                if (self.workers[i].worker_rating.weight) {
                    self.ratedWorkers++;
                }
            }
        }

        function setRating(worker, rating, weight) {
            rating.target = worker;
            RatingService.updateProjectRating(weight, rating, self.resolvedData.id).then(function success(resp) {
                rating.weight = weight;
                getRated();
            }, function error(resp) {
                $mdToast.showSimple('Could not update rating.');
            }).finally(function () {

            });

        }

        function getOtherResponses(task_worker) {
            task_worker.showResponses = !task_worker.showResponses;
            Task.getOtherResponses(task_worker.id).then(function success(resp) {
                task_worker.other_responses = resp[0];
            }, function error(resp) {
                $mdToast.showSimple('Could not get other responses.');
            }).finally(function () {

            });
        }
    }
})();
