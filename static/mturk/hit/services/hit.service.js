/**
 * TaskService
 * @namespace crowdsource.tasks.services
 */
(function () {
    'use strict';

    angular
        .module('mturk.hit.services')
        .factory('HIT', HIT);

    HIT.$inject = ['HttpService'];

    /**
     * @namespace Task
     * @returns {HIT}
     */

    function HIT(HttpService) {
        /**
         * @name HIT
         * @desc The Factory to be returned
         */
        var HIT = {
            retrieve: retrieve
        };

        return HIT;

        function retrieve(id, hit_id) {
            var settings = {
                url: '/mturk/api/hit/',
                method: 'GET',
                params: {
                    task_id: id,
                    hit_id: hit_id
                }
            };
            return HttpService.doRequest(settings);
        }

        function submitTask(data) {
            var settings = {
                url: '/api/task-worker-result/submit-results/',
                method: 'POST',
                data: data
            };
            return HttpService.doRequest(settings);
        }

    }
})();
