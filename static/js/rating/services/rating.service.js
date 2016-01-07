/**
* RatingService
* @namespace crowdsource.rating.services
*/
(function () {
  'use strict';

  angular
    .module('crowdsource.rating.services')
    .factory('RatingService', RatingService);

  RatingService.$inject = ['$cookies', '$q', '$location', 'HttpService'];

  /**
  * @namespace RatingService
  * @returns {Factory}
  */

  function RatingService($cookies, $q, $location, HttpService) {
    /**
    * @name RatingService
    * @desc The Factory to be returned
    */
    var RatingService = {
      getWorkerRatings: getWorkerRatings,
      getWorkerRatingsByModule: getWorkerRatingsByModule,
      getRequesterRatings: getRequesterRatings,
      submitRating: submitRating,
      updateRating: updateRating,
    };

    return RatingService;


    /**
    * @name getWorkerRatings
    * @desc Get worker ratings.
    * @returns {Promise}
    * @memberOf crowdsource.rating.services.RatingService
    */
    function getWorkerRatings() {
      var settings = {
        url: '/api/rating/workers_reviews/',
        method: 'GET'
      };
      return HttpService.doRequest(settings);
    }

    function getWorkerRatingsByProject(project_id) {
        var settings = {
          url: '/api/rating/workers_reviews_by_project/?project='+project_id,
          method: 'GET'
        };

      return HttpService.doRequest(settings);
    }

    function getRequesterRatings() {
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
          project: entry.project
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


  }
})();
