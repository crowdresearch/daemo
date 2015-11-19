(function () {
    'use strict';

    angular
        .module('crowdsource.task.controllers', [])
        .controller('TaskController', TaskController);

    TaskController.$inject = ['$scope', '$location', '$mdToast', '$log', '$http', '$routeParams',
        'Task', 'Authentication', 'Template', '$sce', '$filter', 'Dashboard', '$rootScope', 'RatingService', '$cookies'];

    function TaskController($scope, $location, $mdToast, $log, $http, $routeParams, Task, Authentication, Template, $sce, $filter, Dashboard, $rootScope, RatingService, $cookies) {
        var self = this;
        self.taskData = null;
        self.buildHtml = buildHtml;
        self.skip = skip;
        self.submitOrSave = submitOrSave;
        self.saveComment = saveComment;
        self.handleCheckbox = handleCheckbox;

        activate();

        function activate() {

            self.checkBoxes = {};

            self.task_worker_id = $routeParams.taskWorkerId;
            self.task_id = $routeParams.taskId;

            self.isReturned = $routeParams.hasOwnProperty('returned');

            Dashboard.savedQueue = Dashboard.savedQueue || [];
            Dashboard.savedReturnedQueue = Dashboard.savedReturnedQueue || [];

            self.isSavedQueue = !!Dashboard.savedQueue.length;
            self.isSavedReturnedQueue = !!Dashboard.savedReturnedQueue.length;

            var id = self.task_id;

            if (self.isSavedQueue || self.isSavedReturnedQueue) {
                id = self.task_worker_id;
            }

            Task.getTaskWithData(id, self.isSavedQueue || self.isSavedReturnedQueue).then(function success(data) {
                    self.taskData = data[0].data;
                    self.taskData.id = self.taskData.task ? self.taskData.task : id;
                    angular.forEach(self.taskData.task_template.template_items, function(obj, index){
                        var tabIndex;
                        if(obj.role === "display"){
                            tabIndex = -1;
                        }
                        else {
                            tabIndex = $filter('filter')(self.taskData.task_template.template_items.slice(0, index), {'role': 'input'}).length + 1;
                        }
                        angular.extend(obj, {tabIndex: tabIndex});
                    });
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

        function handleCheckbox(item_id, option) {
            var option = option.trim()
            if (self.checkBoxes.hasOwnProperty(item_id)) {
                var arr = self.checkBoxes[item_id];
                var index = -1;
                for(var i = 0; i < arr.length; i++) {
                    if(arr[i] === option) {
                        index = i; break;
                    }
                }
                if (index == -1) {
                    arr.push(option);
                } else {
                    arr.splice(index, 1);
                }
            } else {
                self.checkBoxes[item_id] = [option];
            }
        }

        function submitOrSave(task_status) {
            var itemsToSubmit = $filter('filter')(self.taskData.task_template.template_items, {role: 'input'});
            var itemAnswers = [];
            angular.forEach(itemsToSubmit, function (obj) {
                if(obj.type === 'checkbox') {
                    if(self.checkBoxes.hasOwnProperty(obj.id) && self.checkBoxes[obj.id].length > 0) {
                        var arr = self.checkBoxes[obj.id];
                        var result = "";
                        for(var i = 0; i < arr.length; i++) {
                            result += arr[i];
                            result += ',';
                        }
                        obj.answer = result.slice(0, result.length - 1)
                    }
                }
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

        self.handleRatingSubmit = function (rating, entry) {
            if (entry.hasOwnProperty('current_rating_id')) {
                RatingService.updateRating(rating, entry).then(function success(resp) {
                    entry.current_rating = rating;
                }, function error(resp) {
                    $mdToast.showSimple('Could not update rating.');
                }).finally(function () {

                });
            } else {
                entry.reviewType = 'worker';
                RatingService.submitRating(rating, entry).then(function success(resp) {
                    entry.current_rating_id = resp[0].id;
                    entry.current_rating = rating;
                }, function error(resp) {
                    $mdToast.showSimple('Could not submit rating.')
                }).finally(function () {

                });
            }
        }
    }
})();


