
(function () {
  'use strict';

  angular
    .module('crowdsource.ranking.controllers')
    .controller('RankingController', RankingController);

  RankingController.$inject = ['$scope', '$log', '$http', 'RankingService'];

  function RankingController($scope, $log, $http, RankingService) {	
  	$scope.ranking = [];
  	$scope.rowCollection=[];

    RankingService.getRequesterRanking().then(
      function success (data,config) {
      	$scope.ranking = data;
      	$scope.rowCollection = data;
      },
      function error (data, status, headers, config) {
      
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

  }

})();