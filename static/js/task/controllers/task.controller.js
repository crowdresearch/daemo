(function () {
    'use strict';

    angular
        .module('crowdsource.task.controllers', [])
        .controller('TaskController', TaskController);

    TaskController.$inject = ['$scope', '$location', '$mdToast', '$log', '$http', '$routeParams',
        'Task', 'Authentication', 'Template', '$sce', '$filter', 'Dashboard'];

    function TaskController($scope, $location, $mdToast, $log, $http, $routeParams, Task, Authentication, Template, $sce, $filter, Dashboard) {
        var self = this;
        self.taskData = null;
        self.buildHtml = buildHtml;
        self.skip = skip;
        self.submitOrSave = submitOrSave;
        self.saveComment = saveComment;

        activate();
        function activate() {
            self.task_worker_id = $routeParams.taskWorkerId;
            self.task_id = $routeParams.taskId;
            if(!self.task_worker_id) { //if they navigate away midqueue and then attempt task from task feed
                Dashboard.savedQueue = [];
            } else if(Dashboard.savedQueue == undefined) { //if they refresh page midqueue
                $location.path('/dashboard');
                return;
            }
            self.isSavedQueue = !!Dashboard.savedQueue.length;
            var id = self.task_worker_id ? self.task_worker_id : self.task_id;
            Task.getTaskWithData(id, self.isSavedQueue).then(function success(data) {
                self.taskData = data[0];
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
            if(self.isSavedQueue) {
                //We drop this task rather than the conventional skip because
                //skip allocates a new task for the worker which we do not want if 
                //they are in the saved queue
                Dashboard.dropSavedTasks({task_ids:[self.task_id]}).then(
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
                saved: self.isSavedQueue
            };
            Task.submitTask(requestData).then(
                function success(data, status) {
                    $location.path(getLocation(task_status, data));
                },
                function error(data, status) {
                    if(task_status == 1) {
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
            if(self.isSavedQueue) {
                Dashboard.savedQueue.splice(0, 1);
                self.isSavedQueue = !!Dashboard.savedQueue.length;
                if(self.isSavedQueue) {
                    return '/task/' + Dashboard.savedQueue[0].task + '/' + Dashboard.savedQueue[0].id;
                } else { //if you finished the queue
                    return '/dashboard';
                }   
            } else {
                if (task_status == 1 || data[1]!=200) { //task is saved or failure
                    return '/';
                } else if (task_status == 2 || task_status == 6) { //submit or skip
                    return '/task/' + data[0].task;
                }
            }
        }
    }
})();


