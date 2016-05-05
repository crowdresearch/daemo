/**
 * ReviewService
 * @namespace crowdsource.review.services
 */
(function () {
    'use strict';

    angular
        .module('crowdsource.review.services')
        .factory('Review', Review);

    Review.$inject = ['$cookies', '$q', 'HttpService'];

    /**
     * @namespace Review
     * @returns {Factory}
     */

    function Review($cookies, $q, HttpService) {
        /**
         * @name ReviewService
         * @desc The Factory to be returned
         */
        var Review = {
            assign:assign,
            get:get,
            update:update
        };

        return Review;

        function assign(taskWorkerResultId) {
            var settings = {
                url: '/api/reviews/',
                method: 'POST',
                data: {
                    taskWorkerResultId: taskWorkerResultId
                }
            };
            return HttpService.doRequest(settings);
        }

        function get(pk) {
            var settings = {
                url: '/api/reviews/'+pk+'/',
                method: 'GET'
            };
            return HttpService.doRequest(settings);
        }

        function update(pk, data) {
            var settings = {
                url: '/api/reviews/'+pk+'/',
                method: 'PUT',
                data:data
            };
            return HttpService.doRequest(settings);
        }



    }
})();
