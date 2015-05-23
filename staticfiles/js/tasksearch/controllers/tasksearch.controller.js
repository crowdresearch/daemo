//__author__ = 'neilthemathguy'

var taskSearchApp = angular.module('crowdsource.tasksearch.controllers', ['smart-table']);

taskSearchApp.controller('taskSearchGridController', ['$scope','$http','$filter', function ($scope,$http,$filter) {
	///API for http get call: api/module/?format=json						
    //Add the http.get to fetchrecords (example see task.controller.js)                    	   



    $scope.displayedCollection = [];
    $scope.rowCollection=[];
	    	$http.get("/api/module/?format=json").success(function(data,config) {
	        	$scope.rowCollection = data;

                $scope.displayedCollection=data;
	    }).error(function(data, status, headers, config) {
	           console.log(status);
	    });
}]);                  