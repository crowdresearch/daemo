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
      getWorkerRankings: getWorkerRankings,
      getWorkerRankingsByModule: getWorkerRankingsByModule,
      getRequesterRankings: getRequesterRankings,
      submitRating: submitRating,
      updateRating: updateRating,
      getRequesterRanking: getRequesterRanking
    };

    return RankingService;


    /**
    * @name getWorkerRankings
    * @desc Get worker rankings.
    * @returns {Promise}
    * @memberOf crowdsource.ranking.services.RankingService
    */
    function getWorkerRankings() {
      var settings = {
        url: '/api/rating/workers_reviews/',
        method: 'GET'
      };
      return HttpService.doRequest(settings);
    }

    function getWorkerRankingsByModule(module_id) {
        var settings = {
          url: '/api/rating/workers_reviews_by_module/?module='+module_id,
          method: 'GET'
        };

      return HttpService.doRequest(settings);
    }

    function getRequesterRankings() {
      var settings = {
        url: '/api/rating/requesters_reviews/',
        method: 'GET'
      };
      return HttpService.doRequest(settings);
    }

    function submitRating(rating, entry) {
      var settings = {
        url: '/api/worker-requester-rating/',
        method: 'POST',
        data: {
          weight: rating,
          origin_type: entry.reviewType,
          target: entry.target,
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
          weight: rating
        }
      };
      return HttpService.doRequest(settings);
    }

    /**
    * @name getRequesterRanking
    * @desc Get requester ranking.
    * @returns {Promise}
    * @memberOf crowdsource.ranking.services.RankingService
    */
    function getRequesterRanking() {
      var settings = {
        url: '/api/requester-ranking/?format=json',
        method: 'GET'
      };
      return HttpService.doRequest(settings);
    }


  }
})();