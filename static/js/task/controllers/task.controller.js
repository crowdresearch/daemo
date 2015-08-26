(function () {
    'use strict';

    angular
        .module('crowdsource.task.controllers', [])
        .controller('TaskController', TaskController);

    TaskController.$inject = ['$scope', '$location', '$mdToast', '$log', '$http', '$routeParams',
        'Task', 'Authentication', 'Template', '$sce', '$filter'];

    function TaskController($scope, $location, $mdToast, $log, $http, $routeParams, Task, Authentication, Template, $sce, $filter) {
        var self = this;
        self.taskData = null;
        self.buildHtml = buildHtml;
        self.skip = skip;
        self.submitOrSave = submitOrSave;
        self.saveComment = saveComment;


        activate();

        function activate() {
            self.task_worker_id = $routeParams.task_worker_id;
            self.task_id = $routeParams.taskId;
            if (self.task_worker_id) {
                Task.getSavedTask(self.task_worker_id).then(function success(data) {
                    self.taskData = data[0];
                    self.taskData.id = self.taskData.task;
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
                }).finally(function () {}
                );
            } else {

                Task.getTaskWithData(self.task_id).then(function success(data) {
                    self.taskData = data[0];
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

        }

        function buildHtml(item) {
            var html = Template.buildHtml(item);
            return $sce.trustAsHtml(html);
        }

        function skip() {
            Task.skipTask(self.task_id).then(function success(data) {
                    if (data[1]==200){
                        $location.path('/task/' + data[0].task);
                    }
                    else {
                        $mdToast.showSimple('No tasks left.');
                    }
                },
                function error(data) {
                    $mdToast.showSimple('Could not skip task.');
                });
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
                task_status: task_status
            };

            if (self.task_worker_id) {
                Task.updateTask(self.task_worker_id, requestData).then(function success(data) {
                    $location.path('/dashboard');
                },
                function error(data) {
                    $mdToast.showSimple('Could not submit/save task.');
                });

                return;
            }



            Task.submitTask(requestData).then(function success(data) {
                    if (task_status == 1 || data[1]!=200) $location.path('/');
                    else if (task_status == 2)
                            $location.path('/task/' + data[0].task);                },
                function error(data) {
                    $mdToast.showSimple('Could not submit/save task.');
                });
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
    }

})();


