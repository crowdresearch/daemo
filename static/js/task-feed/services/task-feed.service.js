/**
 * Project
 * @namespace crowdsource.task-feed.services
 */
(function () {
    'use strict';

    angular
        .module('crowdsource.task-feed.services')
        .factory('TaskFeed', TaskFeed);

    TaskFeed.$inject = ['HttpService'];

    function TaskFeed(HttpService) {

        return {
            getProjects: getProjects
        };

        function getProjects(sortBy) {
            var settings = {
                url: HttpService.apiPrefix + '/projects/task-feed/?sort_by=' + sortBy,
                method: 'GET'
            };
            return HttpService.doRequest(settings);
        }

    }
})();
