
(function () {
  'use strict';

  angular
    .module('crowdsource.ranking.controllers')
    .controller('RankingController', RankingController);

  RankingController.$inject = ['$scope', '$log', '$mdToast', '$http', 'RankingService', 'Authentication'];

  function RankingController($scope, $log, $mdToast, $http, RankingService, Authentication) {
    var self = this;

    getWorkerData();
    getRequesterData();

    function getWorkerData() {
      self.pendingRankings = [];
      RankingService.getWorkerRankings().then(
        function success (resp) {
          var data = resp[0];
          data = data.map(function (item) {
            item.reviewType = 'requester';
            return item;
          });
          self.pendingRankings = data;
        },
        function error (errResp) {
          var data = resp[0];
          $mdToast.showSimple('Could get worker rankings.');
        });
    }

    function getRequesterData() {
      self.requesterRankings = [];
      RankingService.getRequesterRankings().then(
        function success (resp) {
          var data = resp[0];
          data = data.map(function (item) {
            item.reviewType = 'worker';
            return item;
          });
          self.requesterRankings = data;
        },
        function error (errResp) {
          var data = resp[0];
          $mdToast.showSimple('Could get requester rankings.');
        });
    }

    function refreshData(reviewType) {
      if (reviewType === 'worker') {
        getRequesterData();
      } else {
        getWorkerData();
      }
    }

    self.handleRatingSubmit = function (rating, entry) {
      entry.current_rating = rating;
      if (entry.current_rating_id) {
        RankingService.updateRating(rating, entry).then(function success(resp) {
        }, function error (resp) {
          $mdToast.showSimple('Could not update rating.');
        }).finally(function () {
          refreshData(entry.reviewType);
        });
      } else {
        RankingService.submitRating(rating, entry).then(function success(resp) {
        }, function error (resp) {
          $mdToast.showSimple('Could not submit rating.')
        }).finally(function () {
          refreshData(entry.reviewType);
        });
      }

    }

  }

})();