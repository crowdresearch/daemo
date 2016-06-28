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
        self.selectedRevision = null;
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
            Task.getTasks(self.resolvedData.id).then(
                function success(response) {
                    self.loading = false;
                    self.tasks = response[0];
                    loadFirst();
                },
                function error(response) {
                    $mdToast.showSimple('Could not get tasks.');
                }
            ).finally(function () {
            });
        }

        function loadFirst() {
            if (self.tasks.length) {
                listSubmissions(self.tasks[0]);
            }
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
            var item = $filter('filter')(self.resolvedData.template.items,
                {id: resultObj.template_item})[0];
            return item.position;
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
                return resultSet;
            }
            else {
                return result.result;
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

        function setRating(rating, weight) {
            if (rating && rating.hasOwnProperty('id') && rating.id) {
                RatingService.updateRating(weight, rating).then(function success(resp) {
                    rating.weight = weight;
                }, function error(resp) {
                    $mdToast.showSimple('Could not update rating.');
                }).finally(function () {

                });
            } else {
                RatingService.submitRating(weight, rating).then(function success(resp) {
                    rating.id = resp[0].id;
                    rating.weight = weight;
                }, function error(resp) {
                    $mdToast.showSimple('Could not submit rating.')
                }).finally(function () {

                });
            }
        }

        function showActions(workerAlias) {
            return workerAlias.indexOf('mturk') < 0;
        }

        function returnTask(taskWorker, e) {
            if (self.feedback === undefined) {
                self.current_taskWorker = taskWorker;
                showReturnDialog(e);
            } else {
                var request_data = {
                    "task_worker": self.current_taskWorker.id,
                    "body": self.feedback
                };
                Task.submitReturnFeedback(request_data).then(
                    function success(response) {
                        updateStatus(self.status.RETURNED, self.current_taskWorker);
                        self.feedback = undefined;
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
    }
})();
