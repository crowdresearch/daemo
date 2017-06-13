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
        self.selectedTaskId = null;
        self.taskData = null;
        self.selectedTask = null;
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
                    self.nextPage = response[0].next;
                    if (self.nextPage && response[0].up_to) {
                        self.nextPage = self.nextPage + '&up_to=' + response[0].up_to;
                    }
                    retrieveLastOpened();
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


        function acceptAll() {
            Task.acceptAll(self.resolvedData.id).then(
                function success(response) {
                    // var submissionIds = response[0];
                    //
                    // angular.forEach(submissionIds, function (submissionId) {
                    //     var submission = $filter('filter')(self.submissions, {id: submissionId})[0];
                    //     submission.status = self.status.ACCEPTED;
                    // });
                    angular.forEach(self.workers, function (worker) {
                        angular.forEach(worker.tasks, function (task) {
                            if (task.status === self.status.SUBMITTED) {
                                task.status = self.status.ACCEPTED;
                            }
                        });
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
            // var params = {
            //     project_id: self.resolvedData.id
            // };
            window.open('api/file/download-results/?project_id=' + self.resolvedData.id, '_self', '');
            // Task.downloadResults(params).then(
            //     function success(response) {
            //         var headers = response[2]();
            //         console.log(headers);
            //         var filename = headers['x-filename'];
            //
            //         var contentType = headers['content-type'];
            //         var blob = new Blob([response[0]], {type: contentType});
            //
            //         var url = window.URL.createObjectURL(blob);
            //         var a = document.createElement('a');
            //         a.href = url;
            //         // a.href = 'data:text/csv;charset=utf-8,' + response[0].replace(/\n/g, '%0A');
            //         a.target = '_blank';
            //         a.download = "rests.zip";
            //         // a.download = self.resolvedData.name.replace(/\s/g, '_') + '_data.zip';
            //         document.body.appendChild(a);
            //         a.click();
            //     },
            //     function error(response) {
            //
            //     }
            // ).finally(function () {
            // });
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
            if (self.selectedRevision !== self.resolvedData.id) {
                $state.go('project_review', {projectId: self.selectedRevision});
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
