/**
 * Worker
 * @namespace crowdsource.worker.services
 */
(function () {
    'use strict';

    angular
        .module('crowdsource.worker.services')
        .factory('Worker', Worker);

    Worker.$inject = ['$cookies', '$http', '$q', 'HttpService'];

    /**
     * @namespace Worker
     * @returns {Factory}
     */

    function Worker($cookies, $http, $q, HttpService) {
        var Worker = {
            getWorkerPrivateProfile: getWorkerPrivateProfile,
            addSkill: addSkill,
            removeSkill: removeSkill
        };

        return Worker;

        function getWorkerPrivateProfile(profileid) {

            var settings = {
                url: '/api/profile/' + profileid + '/',
                method: 'GET'
            };
            return HttpService.doRequest(settings);
        }

        function addSkill(skillId) {
            var settings = {
                url: '/api/worker-skill/',
                method: 'POST',
                data: {
                    skill: skillId
                }
            };
            return HttpService.doRequest(settings);
        }

        function removeSkill(skillId) {
            var settings = {
                url: '/api/worker-skill/' + skillId + '/',
                method: 'DELETE'
            };
            return HttpService.doRequest(settings);
        }
    }

})();