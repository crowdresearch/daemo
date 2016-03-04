/**
 * RatingService
 * @namespace crowdsource.rating.services
 */
(function () {
    'use strict';

    angular
        .module('crowdsource.rating.services')
        .factory('RatingService', RatingService);

    RatingService.$inject = ['$cookies', '$q', 'HttpService'];

    /**
     * @namespace RatingService
     * @returns {Factory}
     */

    function RatingService($cookies, $q, HttpService) {
        /**
         * @name RatingService
         * @desc The Factory to be returned
         */
        var RatingService = {
            getWorkerRatings: getWorkerRatings,
            getWorkerRatingsByProject: getWorkerRatingsByProject,
            getRequesterRatings: getRequesterRatings,
            submitRating: submitRating,
            updateRating: updateRating,
            listByTarget: listByTarget
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
                url: '/api/rating/workers_ratings_by_project/?project=' + project_id,
                method: 'GET'
            };

            return HttpService.doRequest(settings);
        }

        function getRequesterRatings() {
            var settings = {
                url: '/api/rating/requesters_ratings/',
                method: 'GET'
            };
            return HttpService.doRequest(settings);
        }

        function submitRating(weight, entry) {
            var settings = {
                url: '/api/worker-requester-rating/',
                method: 'POST',
                data: {
                    weight: weight,
                    origin_type: entry.origin_type,
                    target: entry.target
                }
            };
            return HttpService.doRequest(settings);
        }

        function updateRating(weight, entry) {
            var settings = {
                url: '/api/worker-requester-rating/' + entry.id + '/',
                method: 'PUT',
                data: {
                    weight: weight
                }
            };
            return HttpService.doRequest(settings);
        }

        function listByTarget(target, origin_type) {
            var settings = {
                url: '/api/worker-requester-rating/list-by-target/?target=' + target + '&origin_type=' + origin_type,
                method: 'GET'
            };
            return HttpService.doRequest(settings);
        }
    }
})();
