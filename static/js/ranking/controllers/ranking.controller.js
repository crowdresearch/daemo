
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

    self.handleRatingSubmit = function (rating, entry) {

      RankingService.submitRating(rating, entry);
    }

    self.getRatingText = function (ratingNumber) {
      switch(rating) {
        case 1:
          return 'minus';
        case 2:
          return 'neutral';
        case 3:
          return 'plus';
        default:
          return null;
      }
    };

    self.getRatingNumber = function (ratingText) {
      switch(rating) {
        case 1:
          return 'minus';
        case 2:
          return 'neutral';
        case 3:
          return 'plus';
        default:
          return null;
      }
    };

  }

})();