
(function () {
  'use strict';

  angular
    .module('crowdsource.ranking.controllers')
    .controller('RankingController', RankingController);

  RankingController.$inject = ['$scope', '$log', '$mdToast', '$http', 'RankingService'];

  function RankingController($scope, $log, $mdToast, $http, RankingService) {
    var self = this;
  	self.pendingRankings = [];

    RankingService.getPendingRankings().then(
      function success (resp) {
        var data = resp[0];
      	self.pendingRankings = data;
      },
      function error (errResp) {
        var data = resp[0];
        $mdToast.showSimple('Could get pending rankings.');
      });

  }

})();