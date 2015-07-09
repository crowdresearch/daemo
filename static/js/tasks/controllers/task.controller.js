
(function () {
  'use strict';

  angular
    .module('crowdsource.tasks.controllers', ['smart-table'])
    .controller('taskController', taskController);

	taskController.$inject = ['$scope', '$log', '$http', 'TaskService'];

	function taskController($scope, $log, $http, TaskService) {	
  	$scope.displayedCollection = [];
  	$scope.rowCollection=[];

  	TaskService.getModule().then(
  		function success (data,config) {
      	$scope.displayedCollection = data;
      	$scope.rowCollection= data;
			},
			function error (data, status, headers, config) {
			});
	    	
    $scope.gridOptionsTask = {
    multiSelect: false,
    enablePinning: true,
    data:'task',
    columnDefs: [   { field: "name", displayName: 'Name', width: 200, pinned: true },
                    { field: "description", displayName: 'Description', width:150 },
                    { field:"keywords",displayName: 'Keywords', width:190 },
                    { field: "module_timeout", displayName:'Hours Remain', width:130 },
                    { field: "repetition", displayName: 'Repetition', width: 100 },	
                    { field: "price", displayName: 'Pay', width: 60 },	 
                    ]
    };	
	}

})();


