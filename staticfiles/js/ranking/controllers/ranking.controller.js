//@TODO move to serivces 
var rankingApp = angular.module('crowdsource.ranking.controllers', ['ngGrid']);

rankingApp.controller('RankingController', function($scope, $log, $http) {	
    	$scope.selections = [];
    	$scope.ranking = [];
    	$scope.gridOptions = {
    	data:'ranking',
        selectedItems: $scope.selections,
    	multiSelect: false,
    	enablePinning: true,
        columnDefs: [{ field:"Name", width: 200, pinned: true },
                    { field: "Payment", width: 100 },
                    { field: "Fairness", width: 100 },
                    { field: "OperationalSpeed", width: 150 },
                    { field: "Communication", width: 150 },
                    { field: "TotalReviews", width: 140 }
                    ]
    	}
    	
    	$http.get("/requesterranking").success(function(data,config) {
            console.log(data)
        	$scope.ranking = data
    }).error(function(data, status, headers, config) {
           console.log(status)
    });
}) 