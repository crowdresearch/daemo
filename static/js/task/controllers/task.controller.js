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
            var task_id = $routeParams.taskId;
            Task.getTaskWithData(task_id).then(function success(data, status) {
                    self.taskData = data[0];
                },
                function error(data, status) {

                }).finally(function () {

                }
            );
        }
        function buildHtml(item) {
            var html = Template.buildHtml(item);
            return $sce.trustAsHtml(html);
        }
        function skip(){

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

                },
                function error(data, status) {

                }).finally(function () {

                }
            );
        }
	}

})();


