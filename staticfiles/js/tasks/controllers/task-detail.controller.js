
(function () {
  'use strict';

  angular
    .module('crowdsource.tasks.controllers', [])
    .controller('taskDetailController', taskDetailController);

	taskDetailController.$inject = ['$scope', '$location', '$mdToast', '$log', '$http', '$routeParams', 'TaskService', 'Authentication'];

	function taskDetailController($scope, $location, $mdToast, $log, $http, $routeParams, TaskService, Authentication) {	
  	var self = this;
    self.userAccount = Authentication.getAuthenticatedAccount();
    if (!self.userAccount) {
      $location.path('/login');
      return;
    }

    var taskId = $routeParams.taskId;

  	TaskService.getTask(taskId).then(
  		function success (resp) {
        var data = resp[0];
      	// once the tasks are in the DB and not a JSON object in the client-side
        // javascript, we load it dynamically here
        
			},
			function error (resp) {
        var data = resp[0];

			}).finally(function () {
        self.task = {"id": 1, "milestoneDescription": "this is a milestone description", "payment":{"number_of_hits":"10","total":"6.00","wage_per_hit":"0.5","charges":"1"},"selectedCategories":[0,3,4],"name":"Sample project 1","description":"This is my sample description","taskType":"oneTask","upload":"noFile","onetaskTime":"1 hour","template":{"name":"template_bMuDT98e","items":[{"id":"id1","name":"label","type":"label","width":100,"height":100,"values":"Enter Name","role":"display","sub_type":"h4","layout":"column","icon":null,"data_source":null},{"id":"id2","name":"text_field_placeholder1","type":"text_field","width":100,"height":100,"values":null,"role":"display","sub_type":null,"layout":"column","data_source":null},{"id":"id3","name":"label","type":"label","width":100,"height":100,"values":"Enter Place of Birth","role":"display","sub_type":"h4","layout":"column","icon":null,"data_source":null},{"id":"id4","name":"text_field_placeholder2","type":"text_field","width":100,"height":100,"values":null,"role":"display","sub_type":null,"layout":"column","data_source":null},{"id":"id5","name":"label","type":"label","width":100,"height":100,"values":"Favorite Quote","role":"display","sub_type":"h4","layout":"column","icon":null,"data_source":null},{"id":"id6","name":"text_area_placeholder1","type":"text_area","width":100,"height":100,"values":null,"role":"display","sub_type":null,"layout":"column","data_source":null}]}};
      });

    self.acceptTask = function () {
      TaskService.acceptTask(taskId).then(
        function success (resp) {
          var data = resp[0];
          if (data.taskWorkerId) {
            $location.path('/task-worker/' + taskWorkerId);
          } else {
             $mdToast.showSimple('Error registering for task.');
          }
        },
        function error (resp) {
          $mdToast.showSimple('Error attempting task.');
        }).finally(function () {
          $location.path('/task-worker/1');
        });
    };
	    	
	}

})();


