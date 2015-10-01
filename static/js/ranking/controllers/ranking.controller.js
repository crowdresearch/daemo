
(function () {
  'use strict';

  angular
    .module('crowdsource.ranking.controllers')
    .controller('RankingController', RankingController);

  RankingController.$inject = ['$scope', '$log', '$mdToast', '$http', 'RankingService'];

  function RankingController($scope, $log, $mdToast, $http, RankingService) {
  	$scope.ranking = [];
  	$scope.rowCollection=[];

    RankingService.getRequesterRanking().then(
      function success (resp) {
        var data = resp[0];
      	$scope.ranking = data;
      	$scope.rowCollection = data;
      },
      function error (errResp) {
        var data = resp[0];
        $mdToast.showSimple('Could get requester ranking.');
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