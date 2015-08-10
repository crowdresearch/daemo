(function () {
  'use strict';

  angular
    .module('crowdsource.task.controllers', [])
    .controller('TaskController', TaskController);

	TaskController.$inject = ['$scope', '$location', '$mdToast', '$log', '$http', '$routeParams',
    'Task', 'Authentication'];

	function TaskController($scope, $location, $mdToast, $log, $http, $routeParams, Task, Authentication) {
  	    var self = this;
	}

})();


