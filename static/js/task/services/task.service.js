(function () {
    'use strict';

    angular
        .module('crowdsource.task.services')
        .factory('Task', Task);

    Task.$inject = ['HttpService'];


    function Task(HttpService) {
        var baseUrl = HttpService.apiPrefix + '/tasks/';
        var taskWorkerBaseUrl = HttpService.apiPrefix + '/assignments/';
        return {
            list: list,
            getTaskWithData: getTaskWithData,
            preview: preview,
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
            approveWorker: approveWorker,
            listMyTasks: listMyTasks,
            dropSavedTasks: dropSavedTasks,
            submitReturnFeedback: submitReturnFeedback,
            destroy: destroy,
            relaunch: relaunch,
            relaunchAll: relaunchAll,
            getOtherResponses: getOtherResponses,
            attachFile: attachFile,
            reject: reject,
            overrideReturn: overrideReturn
        };

        function attachFile(task_worker_id, template_item_id, file_id) {
            var settings = {
                url: '/api/task-worker-result/attach-file/',
                method: 'POST',
                data: {
                    task_worker_id: task_worker_id,
                    template_item_id: template_item_id,
                    file_id: file_id
                }
            };
            return HttpService.doRequest(settings);
        }

        function list(project_id, offset) {
            var settings = {
                url: baseUrl + 'list-data/?project=' + project_id + '&offset=' + offset,
                method: 'GET'
            };
            return HttpService.doRequest(settings);
        }

        function getTaskWithData(id) {
            var settings = {
                url: baseUrl + id + '/retrieve_with_data/',
                method: 'GET'
            };

            return HttpService.doRequest(settings);
        }

        function preview(id) {
            var settings = {
                url: taskWorkerBaseUrl + id + '/preview/',
                method: 'GET'
            };

            return HttpService.doRequest(settings);
        }

        function getOtherResponses(id) {
            var settings = {
                url: taskWorkerBaseUrl + id + '/other-submissions/',
                method: 'GET'
            };

            return HttpService.doRequest(settings);
        }

        function getPeerReviewTask(id) {
            var settings = {
                url: baseUrl + id + '/retrieve_peer_review/',
                method: 'GET'
            };

            return HttpService.doRequest(settings);
        }

        function destroy(pk) {
            var settings = {
                url: baseUrl + pk + '/',
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
                url: taskWorkerBaseUrl + pk + '/',
                method: 'DELETE'
            };
            return HttpService.doRequest(settings);
        }

        function getTasks(project_id) {
            var settings = {
                url: baseUrl + '?project_id=' + project_id,
                method: 'GET'
            };

            return HttpService.doRequest(settings);
        }

        function updateStatus(request_data) {
            var settings = {
                url: taskWorkerBaseUrl + 'bulk-update-status/',
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
                url: baseUrl + task_id + '/list_comments/',
                method: 'GET'
            };
            return HttpService.doRequest(settings);
        }

        function saveComment(task_id, comment) {
            var settings = {
                url: baseUrl + task_id + '/post_comment/',
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
                url: baseUrl + pk + '/',
                method: 'GET'
            };
            return HttpService.doRequest(settings);
        }

        function listSubmissions(task_id) {
            var settings = {
                url: taskWorkerBaseUrl + 'list-submissions/?task_id=' + task_id,
                method: 'GET'
            };
            return HttpService.doRequest(settings);
        }

        function acceptAll(project_id, upTo) {
            var settings = {
                url: taskWorkerBaseUrl + 'accept-all/?project_id=' + project_id + '&up_to=' + upTo,
                method: 'POST',
                data: {}
            };
            return HttpService.doRequest(settings);
        }

        function approveWorker(project_id, workerId, upTo) {
            var settings = {
                url: taskWorkerBaseUrl + 'approve-worker/?project_id=' + project_id + '&worker_id='
                + workerId + '&up_to=' + upTo,
                method: 'POST',
                data: {}
            };
            return HttpService.doRequest(settings);
        }

        function listMyTasks(project_id) {
            var settings = {
                url: taskWorkerBaseUrl + 'list-my-tasks/?project_id=' + project_id,
                method: 'GET'
            };
            return HttpService.doRequest(settings);
        }

        function dropSavedTasks(data) {
            var settings = {
                url: taskWorkerBaseUrl + 'drop_saved_tasks/',
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
                url: baseUrl + pk + '/relaunch/',
                method: 'POST'
            };
            return HttpService.doRequest(settings);
        }

        function relaunchAll(project_id) {
            var settings = {
                url: baseUrl + 'relaunch-all/?project=' + project_id,
                method: 'POST'
            };
            return HttpService.doRequest(settings);
        }

        function reject(pk, data) {
            var settings = {
                url: taskWorkerBaseUrl + pk + '/reject/',
                method: 'POST',
                data: data
            };
            return HttpService.doRequest(settings);
        }
        function overrideReturn(pk) {
            var settings = {
                url: taskWorkerBaseUrl + pk + '/override-return/',
                method: 'POST',
                data: {}
            };
            return HttpService.doRequest(settings);
        }
    }
})();
