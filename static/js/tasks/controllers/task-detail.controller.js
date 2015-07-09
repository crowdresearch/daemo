
(function () {
  'use strict';

  angular
    .module('crowdsource.tasks.controllers', [])
    .controller('taskDetailController', taskDetailController);

	taskDetailController.$inject = ['$scope', '$location', '$mdToast', '$log', '$http', '$routeParams',
    'TaskService', 'Authentication'];

	function taskDetailController($scope, $location, $mdToast, $log, $http, $routeParams, TaskService,
    Authentication) {	
  
  	var self = this;
    self.userAccount = Authentication.getAuthenticatedAccount();
    if (!self.userAccount) {
      $location.path('/login');
      return;
    }

    var taskId = $routeParams.taskId;
    self.moduleId;

  	TaskService.getTask(taskId).then(
  		function success (resp) {
        var data = resp[0];
        self.moduleId = data.module;
        TaskService.getModule(self.moduleId).then(
          function success (nresp) {
            var nData = nresp[0];
            self.module = nData;
          }, function error (nerr) {
            $mdToast.showSimple('Error loading task.');
          });
			},
			function error (resp) {
        var data = resp[0];

			}).finally(function () {
      });

    self.acceptTask = function () {
      TaskService.acceptTask(self.moduleId).then(
        function success (resp) {
          var data = resp[0];
          if (data.task) {
            $location.path('/task-worker/' + data.task);
          } else {
             $mdToast.showSimple('Error registering for task.');
          }
        },
        function error (resp) {
          var err = resp[0];
          $mdToast.showSimple('Error attempting task ' + JSON.stringify(err));
        }).finally(function () {

        });
    };
	    	
	}

})();


