(function () {
  'use strict';

  angular
    .module('crowdsource.task.controllers', [])
    .controller('TaskController', TaskController);

	TaskController.$inject = ['$scope', '$location', '$mdToast', '$log', '$http', '$routeParams',
    'Task', 'Authentication', 'Template', '$sce'];

	function TaskController($scope, $location, $mdToast, $log, $http, $routeParams, Task, Authentication, Template, $sce) {
  	    var self = this;
        self.taskData = null;
        self.buildHtml = buildHtml;
        activate();

        function activate(){
            var task_id = $routeParams.taskId;
            Task.getTaskWithData(task_id).then(function success(data, status) {
                    console.log(data[0]);
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
	}

})();


