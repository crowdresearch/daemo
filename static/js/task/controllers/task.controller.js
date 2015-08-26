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
                Task.getSavedTask(self.task_worker_id).then(function success(resp) {
                    var data = resp[0];

                    // Modify response to match format.
                    self.taskData = data.task_with_data_and_results;
                    self.taskData.task_template = {
                        template_items: data.task_with_data_and_results.template_items
                    };
                    console.log(self.taskData);
                }, function error (resp) {
                    $mdToast.showSimple('Could not retrieve task worker');
                });
            } else {

                Task.getTaskWithData(self.task_id).then(function success(data, status) {
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
                function error(data, status) {
                    $mdToast.showSimple('Could not get task with data.');
                });
            }

        }

        function buildHtml(item) {
            var html = Template.buildHtml(item);
            return $sce.trustAsHtml(html);
        }

        function skip() {
            Task.skipTask(self.task_id).then(function success(data, status) {
                    $location.path('/task/' + data[0].task);
                },
                function error(data, status) {
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
            Task.submitTask(requestData).then(function success(data, status) {
                    if (task_status == 1) $location.path('/');
                    else if (task_status == 2) $location.path('/task/' + data[0].task);
                },
                function error(data, status) {
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


