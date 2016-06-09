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

    /**
     * @namespace TaskFeed
     * @returns {Factory}
     */

    function TaskFeed($cookies, $http, $q, HttpService) {
        /**
         * @name TaskFeed
         * @desc The Factory to be returned
         */
        var TaskFeed = {
            getProjects: getProjects,
            saveComment: saveComment
        };

        return TaskFeed;

        function getProjects() {
            var settings = {
                url: '/api/project/task-feed/',
                method: 'GET'
            };
            return HttpService.doRequest(settings);
        }

        function saveComment(project_id, comment) {
            var settings = {
                url: '/api/project/' + project_id + '/post-comment/',
                method: 'POST',
                data: {
                    comment: {
                        body: comment
                    }
                }
            };
            return HttpService.doRequest(settings);
        }

    }
})();
