/**
* RankingService
* @namespace crowdsource.ranking.services
*/
(function () {
  'use strict';

  angular
    .module('crowdsource.ranking.services')
    .factory('RankingService', RankingService);

  RankingService.$inject = ['$cookies', '$q', '$location', 'HttpService'];

  /**
  * @namespace RankingService
  * @returns {Factory}
  */

  function RankingService($cookies, $q, $location, HttpService) {
    /**
    * @name RankingService
    * @desc The Factory to be returned
    */
    var RankingService = {
      getPendingRankings: getPendingRankings,
      submitRating: submitRating,
      updateRating: updateRating
    };

    return RankingService;


    /**
    * @name getRequesterRanking
    * @desc Get requester ranking.
    * @returns {Promise}
    * @memberOf crowdsource.ranking.services.RankingService
    */
    function getPendingRankings() {
      var settings = {
        url: '/api/project/workers_reviews/',
        method: 'GET',
      };
      return HttpService.doRequest(settings);
    }

    function submitRating(rating, entry) {
      var settings = {
        url: '/api/worker-requester-rating/',
        method: 'POST',
        data: {
          weight: rating,
          type: 'requester',
          target: entry.worker,
          module: entry.module
        }
      };
      return HttpService.doRequest(settings);
    }

    function updateRating(rating, entry) {
      var settings = {
        url: '/api/worker-requester-rating/' + entry.current_rating_id + '/',
        method: 'PUT',
        data: {
          weight: rating,
          type: 'requester',
          target: entry.worker,
          module: entry.module
        }
      };
      return HttpService.doRequest(settings);
    }


  }
})();