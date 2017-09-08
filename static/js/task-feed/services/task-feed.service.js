/**
 * Project
 * @namespace crowdsource.task-feed.services
 */
(function () {
    'use strict';

    angular
        .module('crowdsource.task-feed.services')
        .factory('TaskFeed', TaskFeed);

    TaskFeed.$inject = ['$cookies', '$http', '$q', 'HttpService'];

    function TaskFeed($cookies, $http, $q, HttpService) {

        return {
            getProjects: getProjects
        };

        function getProjects(sortBy) {
            var settings = {
                url: '/api/project/task-feed/?sort_by=' + sortBy,
                method: 'GET'
            };
            return HttpService.doRequest(settings);
        }

    }
})();
