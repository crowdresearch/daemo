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
        self.submit = submit;

        activate();

        function activate(){
            self.task_id = $routeParams.taskId;
            Task.getTaskWithData(self.task_id).then(function success(data, status) {
                    self.taskData = data[0];
                },
                function error(data, status) {
                    $mdToast.showSimple('Could not get task with data.');
                }).finally(function () {

                }
            );
        }
        function buildHtml(item) {
            var html = Template.buildHtml(item);
            return $sce.trustAsHtml(html);
        }
        function skip(){
            Task.skipTask(self.task_id).then(function success(data, status) {
                    $location.path('/task/'+data[0].task);
                },
                function error(data, status) {
                    $mdToast.showSimple('Could not skip task.');
                }).finally(function () {

                }
            );
        }

        function submit(){
            var itemsToSubmit = $filter('filter')(self.taskData.task_template.template_items, {role: 'input'});
            var itemAnswers = [];
            angular.forEach(itemsToSubmit, function(obj){
                itemAnswers.push(
                    {
                        template_item: obj.id,
                        result: obj.answer
                    }
                );
            });
            var requestData = {
                task: self.taskData.id,
                template_items: itemAnswers
            };
            Task.submitTask(requestData).then(function success(data, status) {
                    $location.path('/task/'+data[0].task);
                },
                function error(data, status) {
                    $mdToast.showSimple('Could not submit task.');
                }).finally(function () {

                }
            );
        }
	}

})();


