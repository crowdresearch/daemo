(function () {
    'use strict';

    angular
        .module('crowdsource.project.controllers')
        .controller('ProjectReviewController', ProjectReviewController);

    ProjectReviewController.$inject = ['$scope', 'Project', 'resolvedData', '$stateParams', 'Task', '$mdToast',
        '$filter', 'RatingService', '$mdDialog', '$state', '$window', '$rootScope'];

    /**
     * @namespace ProjectReviewController
     */
    function ProjectReviewController($scope, Project, resolvedData, $stateParams, Task, $mdToast,
                                     $filter, RatingService, $mdDialog, $state, $window, $rootScope) {
        var self = this;
        self.tasks = [];
        self.loading = true;
        self.loadingSubmissions = true;
        self.submissions = [];
        self.resolvedData = {};
        self.selectedTaskId = null;
        self.taskData = null;
        self.selectedTask = null;
        self.expandCell = expandCell;
        self.acceptAll = acceptAll;
        self.getStatus = getStatus;
        self.updateStatus = updateStatus;
        self.downloadResults = downloadResults;
        self.setRating = setRating;
        self.returnTask = returnTask;
        self.revisionChanged = revisionChanged;
        self.getOtherResponses = getOtherResponses;
        self.selectedRevision = null;
        self.lastOpened = null;
        self.nextPage = null;
        self.loadNextPage = loadNextPage;
        self.getResponse = getResponse;
        self.getHeaders = getHeaders;
        self.getHeaderValues = getHeaderValues;
        self.notAllApproved = notAllApproved;
        self.openTask = openTask;
        self.approveWorker = approveWorker;
        self.demographics = null;
        self.returnStatus = 'return';
        self.sortBy = '-';

        self.upTo = null;
        self.reload = reload;
        self.status = {
            RETURNED: 5,
            REJECTED: 4,
            ACCEPTED: 3,
            SUBMITTED: 2
        };
        activate();
        $scope.$watch('review.sortBy', function (newValue, oldValue) {
            if (!angular.equals(newValue, oldValue) && !self.loading && oldValue.toString() !== '-') {
                reload();
            }

        });

        function activate() {
            self.resolvedData = resolvedData[0];
            if (self.resolvedData) {
                $rootScope.pageTitle = self.resolvedData.name;
            }
            self.selectedRevision = self.resolvedData.id;
            self.revisions = self.resolvedData.revisions;
            Project.getWorkersToRate(self.resolvedData.id, self.sortBy).then(
                function success(response) {
                    self.workers = response[0].workers;
                    self.project_template = response[0].project_template;
                    self.nextPage = response[0].next;
                    if (!self.sortBy || self.sortBy === '-') {
                        self.sortBy = response[0].sort_by;
                    }
                    //
                    self.upTo = response[0].up_to;
                    self.loading = false;
                    if (self.nextPage && response[0].up_to) {
                        self.nextPage = self.nextPage + '&up_to=' + response[0].up_to;
                    }
                    retrieveLastOpened();
                },
                function error(response) {
                    $mdToast.showSimple('Could not fetch workers to rate.');
                }
            ).finally(function () {
                getWorkerDemographics(self.resolvedData.id);
                if (self.resolvedData.is_prototype) {
                    getWorkerFeedback();
                }

            });
        }

        function getWorkerFeedback() {
            Project.getProjectComments(self.resolvedData.id).then(
                function success(response) {
                    self.comments = response[0];
                },
                function error(response) {
                }
            ).finally(function () {
            });
        }

        function getWorkerDemographics() {
            Project.getWorkerDemographics(self.resolvedData.id).then(
                function success(response) {
                    self.demographics = response[0];
                },
                function error(response) {

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

        function approveWorker(worker_id) {
            Task.approveWorker(self.resolvedData.id, worker_id, self.upTo).then(
                function success(response) {
                    var workerTasks = $filter('filter')(self.workers, {"worker": worker_id});
                    if (workerTasks.length && workerTasks[0].hasOwnProperty('tasks')) {
                        angular.forEach(workerTasks[0].tasks, function (task) {
                            if (task.status === self.status.SUBMITTED) {
                                task.status = self.status.ACCEPTED;
                            }
                        });
                    }
                    else {
                        for (var i = 0; i < workerTasks.length; i++) {
                            if (workerTasks[i].status === self.status.SUBMITTED) {
                                workerTasks[i].status = self.status.ACCEPTED;
                            }
                        }
                    }
                }

                ,
                function error(response) {
                    $mdToast.showSimple('Could approve submissions.');
                }
            ).finally(function () {
            });
        }

        function acceptAll() {
            Task.acceptAll(self.resolvedData.id, self.upTo).then(
                function success(response) {
                    angular.forEach(self.workers, function (worker) {
                        if (worker.hasOwnProperty('tasks')) {
                            angular.forEach(worker.tasks, function (task) {
                                if (task.status === self.status.SUBMITTED) {
                                    task.status = self.status.ACCEPTED;
                                }
                            });
                        }
                        else {
                            if (worker.status === self.status.SUBMITTED) {
                                worker.status = self.status.ACCEPTED;
                            }
                        }

                    });
                    $mdToast.showSimple('All remaining submissions were approved.');
                },
                function error(response) {
                    $mdToast.showSimple('Could approve submissions.');
                }
            ).finally(function () {
            });
        }


        function getStatus(statusId) {
            for (var key in self.status) {
                if (self.status.hasOwnProperty(key)) {
                    if (statusId === self.status[key])
                        return key;
                }

            }
        }

        function loadNextPage() {
            if (self.nextPage && !self.loading) {
                self.loading = true;
                Project.getUrl(self.nextPage).then(
                    function success(response) {
                        self.loading = false;
                        self.nextPage = response[0].next;
                        for (var i = 0; i < response[0].workers.length; i++) {
                            var worker = $filter('filter')(self.workers,
                                {worker_alias: response[0].workers[i].worker_alias});
                            if (worker && worker.length) {
                                for (var j = 0; j < response[0].workers[i].tasks.length; j++) {
                                    worker[0].tasks.push(response[0].workers[i].tasks[j]);
                                }
                            }
                            else {
                                self.workers.push(response[0].workers[i]);
                            }
                        }

                    },
                    function error(response) {
                        self.loading = false;
                        $mdToast.showSimple('Could fetch submissions, please reload the page.');
                    }
                ).finally(function () {
                });
            }
        }

        function updateStatus(status, taskWorker) {
            if (taskWorker.status === status) {
                return;
            }
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
            window.open('api/file/download-results/?project_id=' + self.resolvedData.id, '_self', '');
        }

        function returnTask(taskWorker, worker_alias, e) {
            if (taskWorker.status !== self.status.SUBMITTED) {
                return;
            }
            if (!self.feedback) {
                self.current_taskWorker = taskWorker;
                self.current_taskWorker.worker_alias = worker_alias;
                showReturnDialog(e);
            } else {
                var status = self.returnStatus === 'return' ? self.status.RETURNED : self.status.REJECTED;
                var request_data = {
                    "task_worker": self.current_taskWorker.id,
                    "body": self.feedback,
                    "status": status
                };
                Task.submitReturnFeedback(request_data).then(
                    function success(response) {
                        updateStatus(status, self.current_taskWorker);
                        self.feedback = null;
                        self.current_taskWorker.status = status;
                        self.returnStatus = 'return';
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
            if (self.selectedRevision !== self.resolvedData.id) {
                $state.go('project_review', {projectId: self.selectedRevision});
            }
        }


        function setRating(worker, rating, weight) {
            rating.target = worker;
            RatingService.updateProjectRating(weight, rating, self.resolvedData.id).then(function success(resp) {
                rating.weight = weight;
                var worker_tasks = $filter('filter')(self.workers, {'worker': worker});
                for (var i = 0; i < worker_tasks.length; i++) {
                    worker_tasks[i].worker_rating.weight = weight;
                }
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

        function getResponse(task) {
            if (task.results.length) {
                return 'testing';
            }
        }

        function getHeaders(task_data) {
            if (!task_data) {
                return [];
            }
            return Object.keys(task_data);
        }

        function getHeaderValues(task_data) {
            if (!task_data) {
                return [];
            }
            return Object.keys(task_data).map(function (key) {
                return {"value": task_data[key]};
            });
        }

        function notAllApproved(tasks) {
            if (!self.workers) return false;
            var approved = [];
            var returned = [];
            if (tasks) {
                approved = $filter('filter')(tasks, {status: self.status.ACCEPTED});
                returned = $filter('filter')(tasks, {status: self.status.RETURNED});
                return approved.length + returned.length !== tasks.length;
            }
            else {
                if (self.sortBy === 'worker_id') {
                    var notCompleted = false;
                    angular.forEach(self.workers, function (worker) {
                        approved = $filter('filter')(worker.tasks, {status: self.status.ACCEPTED});
                        returned = $filter('filter')(worker.tasks, {status: self.status.RETURNED});
                        if (approved.length + returned.length !== worker.tasks.length) {
                            notCompleted = true;
                        }
                    });
                    return notCompleted;
                }
                else {
                    approved = $filter('filter')(self.workers, {status: self.status.ACCEPTED});
                    returned = $filter('filter')(self.workers, {status: self.status.RETURNED});
                    return approved.length + returned.length !== self.workers.length;
                }
            }
        }

        function reload() {
            self.loading = true;
            self.workers = [];
            activate();
        }

        function openTask(task_worker_id) {
            $window.open('task-preview/' + task_worker_id, '_blank');
        }

        function expandCell(item, index) {
            item.isExpanded = true;
            $rootScope.$emit('expand', {index: index});
        }
    }
})
();
