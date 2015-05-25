//@TODO move to serivces 
//__author__ = 'neilthemathguy'

var rankingApp = angular.module('crowdsource.ranking.controllers', ['ngGrid']);

rankingApp.controller('RankingController', function($scope, $log, $http) {	
    	$scope.ranking = [];
    	$http.get("/api/requesterranking/?format=json").success(function(data,config) {
        	$scope.ranking = data
        	console.log($scope.ranking )
        }).error(function(data, status, headers, config) {
               console.log(status)
        });
    	
    $scope.gridOptions = {
    multiSelect: false,
    enablePinning: true,
    data:'ranking',
    columnDefs: [   
                    { field: "requester_name", displayName: 'Requester Name', width:220,pinned: true },
                    { field:"requester_communicationRank",displayName: 'Communicativity', width:140 },
                    { field: "requester_fairRank", displayName:'Fairness', width:100 },
                    { field: "requester_payRank", displayName: 'Generosity', width: 100 },
                    { field: "requester_speedRank", displayName: 'Promptness', width: 150 },
                    { field: "requester_numberofReviews", displayName: 'Total Reviews',  width: 40 }
                    ]
    };	
}) 


