//@TODO move to serivces 
//__author__ = 'neilthemathguy'

var rankingApp = angular.module('crowdsource.ranking.controllers', ['ngGrid']);

rankingApp.controller('RankingController', function($scope, $log, $http) {	
    	$scope.rankings = [];
    	$http.get("/api/requesterranking/?format=json").success(function(data,config) {
        	$scope.rankings = data
        	console.log($scope.rankings)
        }).error(function(data, status, headers, config) {
               console.log(status)
        });
}) 


