/**
 * TaskService
 * @namespace crowdsource.tasks.services
 */
(function () {
    'use strict';

    angular
        .module('crowdsource.task.services')
        .factory('Task', Task);

    Task.$inject = ['$cookies', '$q', 'HttpService'];

    /**
     * @namespace Task
     * @returns {object}
     */

    function Task($cookies, $q, HttpService) {
        /**
         * @name TaskService
         * @desc The Factory to be returned
         */
        var Task = {
            list: list,
            getTaskWithData: getTaskWithData,
            getPeerReviewTask: getPeerReviewTask,
            submitTask: submitTask,
            skipTask: skipTask,
            getTasks: getTasks,
            updateStatus: updateStatus,
            downloadResults: downloadResults,
            getTaskComments: getTaskComments,
            saveComment: saveComment,
            retrieve: retrieve,
            listSubmissions: listSubmissions,
            acceptAll: acceptAll,
            listMyTasks: listMyTasks,
            dropSavedTasks: dropSavedTasks,
            submitReturnFeedback: submitReturnFeedback,
            destroy: destroy,
            relaunch: relaunch,
            relaunchAll: relaunchAll
        };

        return Task;

        function list(project_id, offset) {
            var settings = {
                url: '/api/task/list-data/?project=' + project_id + '&offset=' + offset,
                method: 'GET'
            };
            return HttpService.doRequest(settings);
        }

        function getTaskWithData(id) {
            var settings = {
                url: '/api/task/' + id + '/retrieve_with_data/',
                method: 'GET'
            };

            return HttpService.doRequest(settings);
        }

        function getPeerReviewTask(id) {
            var settings = {
                url: '/api/task/' + id + '/retrieve_peer_review/',
                method: 'GET'
            };

            return HttpService.doRequest(settings);
        }

        function destroy(pk) {
            var settings = {
                url: '/api/task/' + pk + '/',
                method: 'DELETE'
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

        function skipTask(pk) {
            var settings = {
                url: '/api/task-worker/' + pk + '/',
                method: 'DELETE'
            };
            return HttpService.doRequest(settings);
        }

        function getTasks(project_id) {
            var settings = {
                url: '/api/task/list_by_project/',
                method: 'GET',
                params: {
                    project_id: project_id
                }
            };

            return HttpService.doRequest(settings);
        }

        function updateStatus(request_data) {
            var settings = {
                url: '/api/task-worker/bulk-update-status/',
                method: 'POST',
                data: request_data
            };
            return HttpService.doRequest(settings);
        }

        function downloadResults(params) {
            var settings = {
                url: '/api/file/download-results/',
                method: 'GET',
                params: params
            };
            return HttpService.doRequest(settings);
        }

        function getTaskComments(task_id) {
            var settings = {
                url: '/api/task/' + task_id + '/list_comments/',
                method: 'GET'
            };
            return HttpService.doRequest(settings);
        }

        function saveComment(task_id, comment) {
            var settings = {
                url: '/api/task/' + task_id + '/post_comment/',
                method: 'POST',
                data: {
                    comment: {
                        body: comment
                    }
                }
            };
            return HttpService.doRequest(settings);
        }

        function retrieve(pk) {
            var settings = {
                url: '/api/task/' + pk + '/',
                method: 'GET'
            };
            return HttpService.doRequest(settings);
        }

        function listSubmissions(task_id) {
            var settings = {
                url: '/api/task-worker/list-submissions/?task_id=' + task_id,
                method: 'GET'
            };
            return HttpService.doRequest(settings);
        }

        function acceptAll(task_id) {
            var settings = {
                url: '/api/task-worker/accept-all/?task_id=' + task_id,
                method: 'POST',
                data: {}
            };
            return HttpService.doRequest(settings);
        }

        function listMyTasks(project_id) {
            var settings = {
                url: '/api/task-worker/list-my-tasks/?project_id=' + project_id,
                method: 'GET'
            };
            return HttpService.doRequest(settings);
        }

        function dropSavedTasks(data) {
            var settings = {
                url: '/api/task-worker/drop_saved_tasks/',
                method: 'POST',
                data: data
            };
            return HttpService.doRequest(settings);
        }

        function submitReturnFeedback(data) {
            var settings = {
                url: '/api/return-feedback/',
                method: 'POST',
                data: data
            };
            return HttpService.doRequest(settings);
        }

        function relaunch(pk) {
            var settings = {
                url: '/api/task/' + pk + '/relaunch/',
                method: 'POST'
            };
            return HttpService.doRequest(settings);
        }

        function relaunchAll(project_id) {
            var settings = {
                url: '/api/task/relaunch-all/?project=' + project_id,
                method: 'POST'
            };
            return HttpService.doRequest(settings);
        }
    }
})();
