(function () {
    'use strict';

    angular
        .module('crowdsource.project.controllers')
        .controller('MyTasksController', MyTasksController);

    MyTasksController.$inject = ['$scope', 'Project', 'Task', '$mdToast',
        '$filter', 'RatingService', 'TaskWorker', '$state'];

    /**
     * @namespace MyTasksController
     */
    function MyTasksController($scope, Project, Task, $mdToast, $filter, RatingService, TaskWorker, $state) {
        var self = this;
        self.projects = [];
        self.loading = true;
        self.isSelected = isSelected;
        self.selectedProject = null;
        self.setSelected = setSelected;
        self.getStatus = getStatus;
        self.listMyTasks = listMyTasks;
        self.setRating = setRating;
        self.filterByStatus = filterByStatus;
        self.dropSavedTasks = dropSavedTasks;
        self.getAmount = getAmount;
        self.openTask = openTask;
        self.getDate = getDate;
        self.tasks = [];
        self.status = {
            RETURNED: 5,
            REJECTED: 4,
            ACCEPTED: 3,
            SUBMITTED: 2,
            IN_PROGRESS: 1,
            SKIPPED: 6
        };
        activate();
        function activate() {
            Project.listWorkerProjects().then(
                function success(response) {
                    self.loading = false;
                    self.projects = response[0];
                    //loadFirst();
                },
                function error(response) {
                    $mdToast.showSimple('Could not get tasks.');
                }
            ).finally(function () {
            });
        }
        function getDate(timestamp) {
            return new Date(timestamp).toLocaleString();
        }
        function getAmount(amount) {
            return amount.toFixed(2);
        }


        function isSelected(project) {
            return angular.equals(project, self.selectedProject);
        }

        function setSelected(item) {
            if (angular.equals(item, self.selectedProject)) {
                return null;
            }
            else {
                self.listMyTasks(item);
            }
        }


        function getStatus(statusId) {
            for (var key in self.status) {
                if (self.status.hasOwnProperty(key)) {
                    if (statusId == self.status[key])
                        return key;
                }

            }
        }

        function listMyTasks(project) {
            Task.listMyTasks(project.id).then(
                function success(response) {
                    self.tasks = response[0].tasks;
                    self.selectedProject = project;
                    RatingService.listByTarget(project.owner.id, 'worker').then(
                        function success(response) {
                            self.selectedProject.rating = response[0];
                        },
                        function error(response) {
                            $mdToast.showSimple('Could requester rating');
                        }
                    ).finally(function () {
                    });
                },
                function error(response) {
                    $mdToast.showSimple('Could fetch project tasks');
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

        function filterByStatus(status) {
            return $filter('filter')(self.tasks, {'status': status})
        }

        function dropSavedTasks(task) {
            var request_data = {
                task_ids: [task.task]
            };
            Task.dropSavedTasks(request_data).then(function success(resp) {
                task.status = self.status.SKIPPED;
                $mdToast.showSimple('Task ' + task.task + ' released');
            }, function error(resp) {
                $mdToast.showSimple('Could drop tasks')
            }).finally(function () {
            });
        }

        function openTask(project_id) {
            TaskWorker.attemptAllocateTask(project_id).then(
                function success(data, status) {
                    if (data[1] == 204) {
                        $mdToast.showSimple('No available tasks.');
                        // $state.go('task_feed');
                    }
                    else {
                        var task_id = data[0].task;
                        // var taskWorkerId = data[0].id;
                        $state.go('task', {taskId: task_id});
                    }

                },
                function error(errData) {
                    var err = errData[0];
                    var message = null;
                    if (err.hasOwnProperty('detail')) {
                        message = err.detail;
                    }
                    else {
                        message = JSON.stringify(err);
                    }
                    $mdToast.showSimple('Error: ' + message);
                }
            ).finally(function () {
            });
        }
    }
})();
