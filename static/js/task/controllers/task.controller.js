(function () {
    'use strict';

    angular
        .module('crowdsource.task.controllers', [])
        .controller('TaskController', TaskController);

    TaskController.$inject = ['$scope', '$location', '$mdToast', '$log', '$http', '$routeParams',
        'Task', 'Authentication', 'Template', '$sce', '$filter', 'Dashboard', '$rootScope', 'RankingService'];

    function TaskController($scope, $location, $mdToast, $log, $http, $routeParams, Task, Authentication, Template, $sce, $filter, Dashboard, $rootScope, RankingService) {
        var self = this;
        self.taskData = null;
        self.buildHtml = buildHtml;
        self.skip = skip;
        self.submitOrSave = submitOrSave;
        self.saveComment = saveComment;

        activate();

        self.isPrototype = $rootScope.account.worker_experiment_fields.has_prototype;

        function activate() {
            self.task_worker_id = $routeParams.taskWorkerId;
            self.task_id = $routeParams.taskId;

            self.isReturned = $routeParams.hasOwnProperty('returned');

//            if ((self.isReturned && Dashboard.savedReturnedQueue == undefined) || (!self.isReturned && Dashboard.savedQueue == undefined)) { //if they refresh page mid-queue
//                $location.path('/dashboard');
//                return;
//            }

            Dashboard.savedQueue = Dashboard.savedQueue || [];
            Dashboard.savedReturnedQueue = Dashboard.savedReturnedQueue || [];

            self.isSavedQueue = !!Dashboard.savedQueue.length;
            self.isSavedReturnedQueue = !!Dashboard.savedReturnedQueue.length;

            var id = self.task_id;

            if (self.isSavedQueue || self.isSavedReturnedQueue){
                id = self.task_worker_id;
            }

            Task.getTaskWithData(id, self.isSavedQueue || self.isSavedReturnedQueue).then(function success(data) {
                    

                    self.showRating = $rootScope.account.worker_experiment_fields.pool == 24;
                    if(data[0].hasOwnProperty('rating')){
                        self.rating = data[0].rating[0];
                        self.rating.current_rating = self.rating.weight;
                        self.rating.current_rating_id = self.rating.id;
                    } else {
                        self.rating = {};
                    }
                    self.rating.requester_alias = data[0].requester_alias;
                    self.rating.module = data[0].module;
                    self.rating.target = data[0].target;

                    
                    self.taskData = data[0].data;
                    self.taskData.id = self.taskData.task ? self.taskData.task : id;
                    if (self.taskData.has_comments) {
                        Task.getTaskComments(self.taskData.id).then(
                            function success(data) {
                                angular.extend(self.taskData, {'comments': data[0].comments});
                            },
                            function error(errData) {
                                var err = errData[0];
                                $mdToast.showSimple('Error fetching comments - ' + JSON.stringify(err));
                            }
                        ).finally(function () {
                            });
                    }
                },
                function error(data) {
                    $mdToast.showSimple('Could not get task with data.');
                });


        }

        function buildHtml(item) {
            var html = Template.buildHtml(item);
            return $sce.trustAsHtml(html);
        }

        function skip() {
            if (self.isSavedQueue || self.isSavedReturnedQueue) {
                //We drop this task rather than the conventional skip because
                //skip allocates a new task for the worker which we do not want if 
                //they are in the saved queue
                Dashboard.dropSavedTasks({task_ids: [self.task_id]}).then(
                    function success(data) {
                        $location.path(getLocation(6, data));
                    },
                    function error(data) {
                        $mdToast.showSimple('Could not skip task.');
                    }).finally(function () {

                    }
                );
            } else {
                Task.skipTask(self.task_id).then(
                    function success(data) {
                        $location.path(getLocation(6, data));
                    },
                    function error(data) {
                        $mdToast.showSimple('Could not skip task.');
                    }).finally(function () {

                    }
                );
            }
        }

        function submitOrSave(task_status) {
            var commentExists=false;
            if(self.taskData.comments){
                angular.forEach(self.taskData.comments, function(obj){
                    if(obj.comment.sender == $rootScope.account.profile.id){
                        commentExists = true;
                    }
                });
            }
            if(!commentExists && $rootScope.account.worker_experiment_fields.has_prototype
                && $rootScope.account.worker_experiment_fields.feedback_required){
                    $mdToast.showSimple('Please add feedback and try again ..');
                    return;
            }


            var itemsToSubmit = $filter('filter')(self.taskData.task_template.template_items, {role: 'input'});
            var itemAnswers = [];
            angular.forEach(itemsToSubmit, function (obj) {
                itemAnswers.push(
                    {
                        template_item: obj.id,
                        result: obj.answer
                    }
                );
            });
            var requestData = {
                task: self.taskData.id,
                template_items: itemAnswers,
                task_status: task_status,
                saved: self.isSavedQueue || self.isSavedReturnedQueue
            };
            Task.submitTask(requestData).then(
                function success(data, status) {
                    $location.path(getLocation(task_status, data));
                },
                function error(data, status) {
                    if (task_status == 1) {
                        $mdToast.showSimple('Could not save task.');
                    } else {
                        $mdToast.showSimple('Could not submit task.');
                    }
                }).finally(function () {
                }
            );
        }

        function saveComment() {
            Task.saveComment(self.taskData.id, self.comment.body).then(
                function success(data) {
                    if (self.taskData.comments == undefined) {
                        angular.extend(self.taskData, {'comments': []});
                    }
                    self.taskData.comments.push(data[0]);
                    self.comment.body = null;
                },
                function error(errData) {
                    var err = errData[0];
                    $mdToast.showSimple('Error saving comment - ' + JSON.stringify(err));
                });
        }

        function getLocation(task_status, data) {
            if (self.isSavedQueue) {
                Dashboard.savedQueue.splice(0, 1);
                self.isSavedQueue = !!Dashboard.savedQueue.length;
                if (self.isSavedQueue) {
                    return '/task/' + Dashboard.savedQueue[0].task + '/' + Dashboard.savedQueue[0].id;
                } else { //if you finished the queue
                    return '/dashboard';
                }
            } else {
                if (self.isSavedReturnedQueue) {
                    Dashboard.savedReturnedQueue.splice(0, 1);
                    self.isSavedReturnedQueue = !!Dashboard.savedReturnedQueue.length;
                    if (self.isSavedReturnedQueue) {
                        return '/task/' + Dashboard.savedReturnedQueue[0].task + '/' + Dashboard.savedReturnedQueue[0].id;
                    } else { //if you finished the queue
                        return '/dashboard';
                    }
                }
                else {

                    if (task_status == 1 || data[1] != 200) { //task is saved or failure
                        return '/';
                    } else if (task_status == 2 || task_status == 6) { //submit or skip
                        return '/task/' + data[0].task;
                    }
                }
            }
        }

        self.handleRatingSubmit = function(rating, entry) {
            if (entry.hasOwnProperty('current_rating_id')) {
                RankingService.updateRating(rating, entry).then(function success(resp) {
                    entry.current_rating = rating;
                }, function error(resp) {
                    $mdToast.showSimple('Could not update rating.');
                }).finally(function () {

                });
            } else {
                entry.reviewType = 'worker';
                RankingService.submitRating(rating, entry).then(function success(resp) {
                    entry.current_rating_id = resp[0].id
                    entry.current_rating = rating;
                }, function error(resp) {
                    $mdToast.showSimple('Could not submit rating.')
                }).finally(function () {

                });
            }
        }
    }
})();


