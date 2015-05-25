//neilthemathguy @TODO add serverice 
	var rankingApp = angular.module('crowdsource.tasks.controllers', ['ngGrid']);

	rankingApp.controller('taskController', function($scope, $log, $http) {	
	    	$scope.task = [];
	    	$http.get("/api/module/?format=json").success(function(data,config) {
	        	$scope.task = data
	        	console.log($scope.task)
	    }).error(function(data, status, headers, config) {
	           console.log(status)
	    });
	});


