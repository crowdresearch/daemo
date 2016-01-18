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
            get_or_create: get_or_create
        };

        return HIT;

        function get_or_create(taskId, hitId, assigmentId, workerId) {
            var settings = {
                url: '/api/mturk/',
                method: 'POST',
                data: {
                    taskId: taskId,
                    hitId: hitId,
                    assignmentId: assigmentId,
                    workerId: workerId
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
