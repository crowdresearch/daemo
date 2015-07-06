
(function () {
  'use strict';

  angular
    .module('crowdsource.tasks.controllers', [])
    .controller('taskDetailController', taskDetailController);

	taskDetailController.$inject = ['$scope', '$log', '$http', '$routeParams', 'TaskService'];

	function taskDetailController($scope, $log, $http, $routeParams, TaskService) {	
  	$scope.task = null;

  	TaskService.getModule().then(
  		function success (data,config) {
      	// once the tasks are in the DB and not a JSON object in the client-side
        // javascript, we load it dynamically here
        
			},
			function error (data, status, headers, config) {
			});
	    	
	}

})();


