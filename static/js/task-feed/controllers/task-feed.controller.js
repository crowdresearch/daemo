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
        self.currentPage = 1;
        self.page_data = {};
        self.page_numbers = [];
        self.switchPage = switchPage;
        self.getCollection = getCollection;
        self.has_pagination = has_pagination;
        TaskFeed.getProjects().then(
            function success(data) {
                self.projects = data[0];
                self.availableTasks = false;
                self.processedProjects = [];
                var k = 0;
                var q = 0;
                var page = [];
                //experiment code -- pagination
                for (var i = 0; i < self.projects.length; i++) {
                    if (self.projects[i].modules_filtered.length && self.projects[i].modules_filtered[0].available_tasks != 0){
                        self.processedProjects.push(self.projects[i]);
                    }
                }
                for (var i = 0; i< self.processedProjects.length; i++){
                    page.push(self.processedProjects[i]);
                    if (((i + 1) % 5) == 0 || self.processedProjects.length - i == 1) {
                        k++;
                        self.page_data[k] = page;
                        page = [];
                        self.page_numbers.push(k);
                    }
                }
                for (var i = 0; i < self.projects.length; i++) {
                    for (var j = 0; j < self.projects[i].modules_filtered.length; j++) {
                        if (self.projects[i].modules_filtered[j].available_tasks != 0) {
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

        function switchPage(index) {
            var random = Math.floor(Math.random() * (3)) + 2;
            $mdToast.showSimple('Loading...');
            setTimeout(function () {
                self.currentPage = index;
                $scope.$apply();
            }, random*1000);
        }

        function getCollection(){
            if(has_pagination()){
                return self.page_data[self.currentPage];
            }
            return self.projects;
        }

        function has_pagination(){
            var fields = $rootScope.account.worker_experiment_fields;
            if(fields)
                return (fields.sorting_type===1);
            return false;
        }
    }

})
();