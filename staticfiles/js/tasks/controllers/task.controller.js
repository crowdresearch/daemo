//neilthemathguy @TODO add serverice 
	var rankingApp = angular.module('crowdsource.tasks.controllers', ['smart-table']);

	rankingApp.controller('taskController', function($scope, $log, $http) {	
	    	$scope.displayedCollection = [];
	    	$scope.rowCollection=[];
	    	$http.get("/api/module/?format=json").success(function(data,config) {
	        	$scope.displayedCollection = data;
	        	$scope.rowCollection= data;
	        	console.log($scope.displayedCollection)
	    }).error(function(data, status, headers, config) {
	           console.log(status)
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
	});


