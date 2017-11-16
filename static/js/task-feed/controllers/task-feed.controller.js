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

    TaskFeedController.$inject = ['$window', '$state', '$scope', '$mdToast', 'TaskFeed',
        '$filter', 'Authentication', 'TaskWorker', 'Project', '$rootScope', '$stateParams', '$mdMedia'];

    /**
     * @namespace TaskFeedController
     */
    function TaskFeedController($window, $state, $scope, $mdToast, TaskFeed,
                                $filter, Authentication, TaskWorker, Project, $rootScope, $stateParams, $mdMedia) {

        var userAccount = Authentication.getAuthenticatedAccount();

        var self = this;
        self.sortBy = '-';
        // $scope.screenIsSmall = $mdMedia('sm');
        self.projects = [];
        self.previewedProject = null;
        self.showPreview = showPreview;
        self.openTask = openTask;
        self.openComments = openComments;
        self.saveComment = saveComment;
        self.loading = true;
        self.getStatusName = getStatusName;
        self.getRatingPercentage = getRatingPercentage;
        self.openChat = openChat;
        self.remainingCount = 0;
        self.hasPermission = false;
        // self.discuss = discuss;

        activate();
        $scope.$watch('taskfeed.sortBy', function (newValue, oldValue) {
            if (!angular.equals(newValue, oldValue) && !self.loading && oldValue.toString() !== '-') {
                getProjects();
            }

        });

        function activate() {
            if ($stateParams.projectId) {
                Project.hasPermission($stateParams.projectId).then(
                    function success(data) {
                        self.hasPermission = true;
                    },
                    function error(errData) {
                        self.hasPermission = false;
                    });
                Project.getPreview($stateParams.projectId).then(
                    function success(data) {
                        self.previewedProject = data[0];
                        self.previewedProject.task.template.items = sortItems(self.previewedProject.task.template.items);
                        self.loading = false;
                        if (data[0]) {
                            $rootScope.pageTitle = data[0].name;
                        }
                    },
                    function error(errData) {
                        $mdToast.showSimple('Error fetching preview.');
                    }
                ).finally(function () {
                    Project.logPreview($stateParams.projectId).then(
                        function success(data) {

                        }
                    ).finally(function () {
                    });
                });

                Project.getRemainingCount($stateParams.projectId).then(
                    function success(data) {
                        self.remainingCount = data[0].remaining;
                    },
                    function error(errData) {
                    }
                ).finally(function () {
                });

            }
            else {
                getProjects();
            }
        }

        function sortItems(items) {
            var results = [];
            var firstItems = $filter('filter')(items, {predecessor: null});
            angular.forEach(firstItems, function (item) {
                results.push(item);
                var next = $filter('filter')(items, {predecessor: item.id});
                while (next && next.length) {
                    var temp = next.pop();
                    results.push(temp);
                    var successors = $filter('filter')(items, {predecessor: temp.id});
                    if (successors && successors.length) {
                        angular.forEach(successors, function (obj) {
                            next.push(obj);
                        })
                    }
                }
            });
            return results;
        }

        function getProjects() {
            self.loading = true;

            TaskFeed.getProjects(self.sortBy).then(
                function success(data) {
                    self.projects = data[0].results.filter(function (project) {
                        return project.available_tasks > 0;
                    });
                    if (!self.sortBy || self.sortBy === '-') {
                        self.sortBy = data[0].sort_by;
                    }
                    self.availableTasks = self.projects.length > 0;
                },
                function error(errData) {
                    self.error = errData[0].detail;
                    $mdToast.showSimple('Could not fetch projects.');
                }
            ).finally(function () {
                self.loading = false;
            });
        }

        function showPreview(project) {
            if (project.template && project.show_preview) {
                project.show_preview = false;
            }
            else if (project.template && !project.show_preview) {
                project.show_preview = true;
            }
            else {
                project.show_preview = true;
                Project.getPreview(project.id).then(
                    function success(data) {
                        angular.extend(project, {'template': data[0].template});
                        project.show_preview = true;
                    },
                    function error(errData) {
                        var err = errData[0];
                        $mdToast.showSimple('Error fetching preview.');
                    }
                ).finally(function () {
                });
            }
        }

        function openTask(project_id) {
            TaskWorker.attemptAllocateTask(project_id).then(
                function success(data, status) {
                    if (data[1] == 204) {
                        $mdToast.showSimple('Error: No more tasks left.');
                        $state.go('task_feed');
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

        function getRatingPercentage(rating, raw_rating, circle) {
            if (raw_rating) rating = raw_rating;
            return rating >= circle ? 100 : rating >= circle - 1 ? (rating - circle + 1) * 100 : 0;
        }

        function openChat(requester) {
            $rootScope.openChat(requester);
        }

        // function discuss(project) {
        //     Project.openDiscussion(project.id).then(
        //         function success(data) {
        //             angular.extend(project, {'discussion_link': data[0].link});
        //
        //             function open(project) {
        //                 $window.open(project.discussion_link, '_blank');
        //             }
        //
        //             function openInNewTab(project) {
        //                 var uri = project.discussion_link;
        //                 var link = angular.element('<a href="' + uri + '" target="_blank"></a>');
        //
        //                 angular.element(document.body).append(link);
        //
        //                 link[0].click();
        //                 link.remove();
        //             }
        //
        //
        //             openInNewTab(project);
        //         },
        //         function error(errData) {
        //             var err = errData[0];
        //             $mdToast.showSimple('Error opening discussion');
        //         }
        //     ).finally(function () {
        //     });
        // }
    }

})
();
