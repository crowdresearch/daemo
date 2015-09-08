//__author__ = 'neilthemathguy'

(function () {
  'use strict';

	angular
	    .module('crowdsource.tasksearch.controllers', [])
	    .controller('taskSearchGridController', taskSearchGridController);

	taskSearchGridController.$inject = ['$scope','$http','$filter', '$mdToast', 'TaskSearchService'];

	function taskSearchGridController($scope, $http, $filter, $mdToast, TaskSearchService) {
		///API for http get call: api/module/?format=json						
	    //Add the http.get to fetchrecords (example see task.controller.js)                    	   

	    $scope.displayedCollection = [];
	    $scope.rowCollection=[];

	    TaskSearchService.getModule().then(
	    	function success(data) {
	      	$scope.rowCollection = data;
	        $scope.displayedCollection=data;
	    	},
		    function error(data) {
		    	$mdToast.showSimple('Could not get module.');
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