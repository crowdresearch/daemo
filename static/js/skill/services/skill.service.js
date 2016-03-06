/**
 * Skill
 * @namespace crowdsource.skill.services
 */
(function () {
    'use strict';

    angular
        .module('crowdsource.skill.services')
        .factory('Skill', Skill);

    Skill.$inject = ['$q', 'HttpService'];

    /**
     * @namespace Skill
     * @returns {Factory}
     */

    function Skill($q, HttpService) {
        var Skill = {
            getAllSkills: getAllSkills
        };

        function getAllSkills() {
            var settings = {
                url: '/api/skill/',
                method: 'GET'
            };
            return HttpService.doRequest(settings);
        }


        return Skill;
    }

})();