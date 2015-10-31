/**
 * TaskFeedController
 * @namespace crowdsource.task-feed.controllers
 * @author dmorina
 */
(function () {
    'use strict';

    angular
        .module('crowdsource.task-feed.controllers')
        .controller('TaskFeedController', TaskFeedController);

    TaskFeedController.$inject = ['$window', '$location', '$scope', '$mdToast', 'TaskFeed',
        '$filter', 'Authentication', 'TaskWorker', 'Project', '$rootScope'];

    /**
     * @namespace TaskFeedController
     */
    function TaskFeedController($window, $location, $scope, $mdToast, TaskFeed,
                                $filter, Authentication, TaskWorker, Project, $rootScope) {
        var userAccount = Authentication.getAuthenticatedAccount();
        if (!userAccount) {
            $location.path('/login');
            return;
        }

        var self = this;
        self.toggleBookmark = toggleBookmark;
        self.projects = [];
        self.previewedModule = null;
        self.showPreview = showPreview;
        self.openTask = openTask;
        self.openComments = openComments;
        self.saveComment = saveComment;
        self.loading = true;
        self.getStatusName = getStatusName;

        TaskFeed.getProjects().then(
            function success(data) {
                self.projects = data[0];
                self.availableTasks = false;
                for (var i = 0; i < self.projects.length; i++) {
                    for (var j = 0; j < self.projects[i].modules.length; j++) {
                        if (self.projects[i].modules[j].available_tasks != 0) {
                            self.availableTasks = true;
                            return;
                        }
                    }
                }


            },
            function error(errData) {
                self.error = errData[0].detail;
                $mdToast.showSimple('Could not get task with data.');
            }
        ).
            finally(function () {
                self.loading = false;
            });

        function toggleBookmark(project) {
            project.is_bookmarked = !project.is_bookmarked;
        }

        function showPreview(module) {
            self.previewedModule = module;
        }

        function openTask(module_id) {
            TaskWorker.attemptAllocateTask(module_id).then(
                function success(data) {
                    var task_id = data[0].task;
                    var taskWorkerId = data[0].id;
                    $location.path('/task/' + task_id + '/' + taskWorkerId);
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

        function openComments(module) {
            if (module.comments && module.is_comment_expanded) {
                module.is_comment_expanded = false;
            }
            else if (module.comments && !module.is_comment_expanded) {
                module.is_comment_expanded = true;
            }
            else {
                Project.getModuleComments(module.id).then(
                    function success(data) {
                        angular.extend(module, {'comments': data[0].comments});
                        module.is_comment_expanded = true;
                    },
                    function error(errData) {
                        var err = errData[0];
                        $mdToast.showSimple('Error fetching comments - ' + JSON.stringify(err));
                    }
                ).finally(function () {
                    });
            }
        }

        function saveComment(module) {
            TaskFeed.saveComment(module.id, self.comment.body).then(
                function success(data) {
                    if (module.comments == undefined) {
                        angular.extend(module, {'comments': []});
                    }
                    module.comments.push(data[0]);
                    self.comment.body = null;
                },
                function error(errData) {
                    var err = errData[0];
                    $mdToast.showSimple('Error saving comment - ' + JSON.stringify(err));
                }
            ).finally(function () {
                });
        }

        function getStatusName(statusId) {
            if (statusId == 5) return 'Paused';
            else if (statusId == 4) return 'Completed';
            else return 'Running';
        }
    }

})
();