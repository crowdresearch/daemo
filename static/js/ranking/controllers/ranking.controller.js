
(function () {
  'use strict';

  angular
    .module('crowdsource.ranking.controllers')
    .controller('RankingController', RankingController);

  RankingController.$inject = ['$scope', '$log', '$mdToast', '$http', 'RankingService', 'Authentication'];

  function RankingController($scope, $log, $mdToast, $http, RankingService, Authentication) {
    var self = this;

    self.ratingStates = [
        {stateOn: 'check-minus-on', stateOff: 'check-minus-off'},
        {stateOn: 'check-on', stateOff: 'check-off'},
        {stateOn: 'check-plus-on', stateOff: 'check-plus-off'}
    ];

    getData();

    function getData() {
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

    self.handleRatingSubmit = function (rating, entry) {
      entry.current_rating = rating;
      if (entry.id) {
        RankingService.updateRating(rating, entry).then(function success(resp) {
          getData();
        }, function error (resp) {
          getData();
          $mdToast.showSimple('Could not update rating.');
        });
      } else {
        RankingService.submitRating(rating, entry).then(function success(resp) {
          getData();
        }, function error (resp) {
          getData();
          $mdToast.showSimple('Could not submit rating.')
        });
      }

    }

  }

})();