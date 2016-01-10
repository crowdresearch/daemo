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
        '$filter', 'Authentication', 'TaskWorker', 'Project', '$rootScope', '$routeParams'];

    /**
     * @namespace TaskFeedController
     */
    function TaskFeedController($window, $location, $scope, $mdToast, TaskFeed,
                                $filter, Authentication, TaskWorker, Project, $rootScope, $routeParams) {
        var userAccount = Authentication.getAuthenticatedAccount();
        if (!userAccount) {
            $location.path('/login');
            return;
        }

        var self = this;
        self.projects = [];
        self.previewedProject = null;
        self.showPreview = showPreview;
        self.openTask = openTask;
        self.openComments = openComments;
        self.saveComment = saveComment;
        self.loading = true;
        self.getStatusName = getStatusName;
        self.openRequesterProfile = openRequesterProfile;
        activate();

        function activate(){
            if($routeParams.projectId){
                self.openTask($routeParams.projectId);
            }
            else{
                getProjects();
            }
        }
        function getProjects() {
            TaskFeed.getProjects().then(
                function success(data) {
                    self.projects = data[0];
                    self.availableTasks = false;
                    for (var j = 0; j < self.projects.length; j++) {
                        if (self.projects[j].available_tasks != 0) {
                            self.availableTasks = true;
                            return;
                        }
                    }
                },
                function error(errData) {
                    self.error = errData[0].detail;
                    $mdToast.showSimple('Could projects.');
                }
            ).
            finally(function () {
                self.loading = false;
            });
        }

        function showPreview(project) {
            if (project.task_template && project.show_preview) {
                project.show_preview = false;
            }
            else if (project.task_template && !project.show_preview) {
                project.show_preview = true;
            }
            else {
                project.show_preview = true;
                Project.getPreview(project.id).then(
                    function success(data) {
                        angular.extend(project, {'task_template': data[0].task_template});
                        project.show_preview = true;
                    },
                    function error(errData) {
                        var err = errData[0];
                        $mdToast.showSimple('Error fetching preview - ' + JSON.stringify(err));
                    }
                ).finally(function () {});
            }
        }

        function openTask(project_id) {
            TaskWorker.attemptAllocateTask(project_id).then(
                function success(data, status) {
                    if(data[1]==204){
                        $mdToast.showSimple('Error: No more tasks left.');
                        $location.path('/task-feed');
                    }
                    else{
                        var task_id = data[0].task;
                        var taskWorkerId = data[0].id;
                        $location.path('/task/' + task_id + '/' + taskWorkerId);
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

        function openComments(project) {
            if (project.comments && project.is_comment_expanded) {
                project.is_comment_expanded = false;
            }
            else if (project.comments && !project.is_comment_expanded) {
                project.is_comment_expanded = true;
            }
            else {
                Project.getProjectComments(project.id).then(
                    function success(data) {
                        angular.extend(project, {'comments': data[0].comments});
                        project.is_comment_expanded = true;
                    },
                    function error(errData) {
                        var err = errData[0];
                        $mdToast.showSimple('Error fetching comments - ' + JSON.stringify(err));
                    }
                ).finally(function () {
                    });
            }
        }

        function saveComment(project) {
            TaskFeed.saveComment(project.id, self.comment.body).then(
                function success(data) {
                    if (project.comments == undefined) {
                        angular.extend(project, {'comments': []});
                    }
                    project.comments.push(data[0]);
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

        function openRequesterProfile(requester) {
            $location.path('/profile/' + requester.id);
        }

    }

})
();
