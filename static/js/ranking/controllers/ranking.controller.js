
(function () {
  'use strict';

  angular
    .module('crowdsource.ranking.controllers')
    .controller('RankingController', RankingController);

  RankingController.$inject = ['$scope', '$log', '$mdToast', '$http', 'RankingService'];

  function RankingController($scope, $log, $mdToast, $http, RankingService) {
    var self = this;
  	self.pendingRankings = [];

    self.ratingStates = [
        {stateOn: 'check-minus-on', stateOff: 'check-minus-off'},
        {stateOn: 'check-on', stateOff: 'check-off'},
        {stateOn: 'check-plus-on', stateOff: 'check-plus-off'}
    ];

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