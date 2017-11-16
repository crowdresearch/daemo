(function () {
    'use strict';

    angular
        .module('crowdsource.project.services')
        .factory('Project', Project);

    Project.$inject = ['HttpService'];

    function Project(HttpService) {
        var baseUrl = HttpService.apiPrefix + '/projects/';
        return {
            getRequesterProjects: listRequesterProjects,
            listWorkerProjects: listWorkerProjects,
            retrieve: retrieve,
            create: create,
            update: update,
            deleteInstance: deleteInstance,
            attachFile: attachFile,
            deleteFile: deleteFile,
            fork: fork,
            getProjectComments: getProjectComments,

            getPreview: getPreview,
            getFeedback: getFeedback,
            postComment: postComment,
            updateComment: updateComment,
            createQualification: createQualification,
            createQualificationItem: createQualificationItem,
            deleteQualificationItem: deleteQualificationItem,
            updateQualificationItem: updateQualificationItem,
            getQualificationItems: getQualificationItems,
            createRevision: createRevision,
            publish: publish,
            get_relaunch_info: get_relaunch_info,
            updateStatus: updateStatus,
            getWorkersToRate: getWorkersToRate,
            getWorkersToReview: getWorkersToReview,
            lastOpened: lastOpened,
            status: status,
            getUrl: getUrl,
            retrievePaymentInfo: retrievePaymentInfo,
            retrieveSubmittedTasksCount: retrieveSubmittedTasksCount,
            openDiscussion: openDiscussion,
            recreateTasks: recreateTasks,
            getTimeEstimates: getTimeEstimates,
            getWorkerDemographics: getWorkerDemographics,
            getRemainingCount: getRemainingCount,
            hasPermission: hasPermission,
            logPreview: logPreview
        };


        function create() {
            var settings = {
                url: baseUrl + '?with_defaults=1',
                method: 'POST'
            };
            return HttpService.doRequest(settings);
        }

        function update(pk, data, path) {
            var settings = {
                url: baseUrl + pk + '/',
                method: 'PUT',
                data: data
            };
            return HttpService.doRequest(settings);
        }

        function publish(pk, data) {
            var settings = {
                url: baseUrl + pk + '/publish/',
                method: 'POST',
                data: data
            };
            return HttpService.doRequest(settings);
        }

        function updateStatus(pk, data) {
            var settings = {
                url: baseUrl + pk + '/update_status/',
                method: 'PUT',
                data: data
            };
            return HttpService.doRequest(settings);
        }

        function recreateTasks(pk, data) {
            var settings = {
                url: baseUrl + pk + '/recreate_tasks/',
                method: 'POST',
                data: data
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

        function retrievePaymentInfo(pk) {
            var settings = {
                url: baseUrl + pk + '/payment/',
                method: 'GET'
            };
            return HttpService.doRequest(settings);
        }

        function retrieveSubmittedTasksCount(pk) {
            var settings = {
                url: baseUrl + pk + '/submitted-tasks-count/',
                method: 'GET'
            };
            return HttpService.doRequest(settings);
        }

        function lastOpened(pk) {
            var settings = {
                url: baseUrl + pk + '/last-opened/',
                method: 'GET'
            };
            return HttpService.doRequest(settings);
        }

        function status(pk) {
            var settings = {
                url: baseUrl + pk + '/status/',
                method: 'GET'
            };
            return HttpService.doRequest(settings);
        }

        function get_relaunch_info(pk) {
            var settings = {
                url: baseUrl + pk + '/relaunch-info/',
                method: 'GET'
            };
            return HttpService.doRequest(settings);
        }

        function getWorkersToRate(pk, sortBy) {
            var settings = {
                url: baseUrl + pk + '/rate-submissions/?sort_by=' + sortBy,
                method: 'GET'
            };
            return HttpService.doRequest(settings);
        }

        function getUrl(url) {
            var settings = {
                url: url,
                method: 'GET'
            };
            return HttpService.doRequest(settings);
        }

        function getWorkersToReview(pk) {
            var settings = {
                url: baseUrl + pk + '/review-submissions/',
                method: 'GET'
            };
            return HttpService.doRequest(settings);
        }

        function deleteInstance(pk) {
            var settings = {
                url: baseUrl + pk + '/',
                method: 'DELETE'
            };
            return HttpService.doRequest(settings);
        }


        function attachFile(pk, data) {
            var settings = {
                url: baseUrl + pk + '/attach_file/',
                method: 'POST',
                data: data
            };
            return HttpService.doRequest(settings);
        }

        function logPreview(pk) {
            var settings = {
                url: baseUrl + pk + '/log-preview/',
                method: 'POST',
                data: {}
            };
            return HttpService.doRequest(settings);
        }

        function deleteFile(pk, data) {
            var settings = {
                url: baseUrl + pk + '/delete_file/',
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json'
                },
                data: data
            };
            return HttpService.doRequest(settings);
        }

        function fork(pk) {
            var settings = {
                url: baseUrl + pk + '/fork/',
                method: 'POST'
            };
            return HttpService.doRequest(settings);
        }

        function getProjectComments(pk) {
            var settings = {
                url: baseUrl + pk + '/comments/',
                method: 'GET'
            };
            return HttpService.doRequest(settings);
        }

        function listWorkerProjects() {
            var settings = {
                url: baseUrl + '?group_by=status',
                method: 'GET'
            };
            return HttpService.doRequest(settings);
        }

        function listRequesterProjects() {
            var settings = {
                url: baseUrl + '?account_type=requester',
                method: 'GET'
            };
            return HttpService.doRequest(settings);
        }

        function getPreview(pk) {
            var settings = {
                url: baseUrl + pk + '/preview/',
                method: 'GET'
            };
            return HttpService.doRequest(settings);
        }

        function createRevision(pk) {
            var settings = {
                url: baseUrl + pk + '/create-revision/',
                method: 'POST',
                data: {}
            };
            return HttpService.doRequest(settings);
        }

        function createQualificationItem(data) {
            var settings = {
                url: '/api/qualification-item/',
                method: 'POST',
                data: data
            };
            return HttpService.doRequest(settings);
        }

        function deleteQualificationItem(pk) {
            var settings = {
                url: '/api/qualification-item/' + pk + '/',
                method: 'DELETE'
            };
            return HttpService.doRequest(settings);
        }

        function updateQualificationItem(pk, expression) {
            var settings = {
                url: '/api/qualification-item/' + pk + '/',
                method: 'PUT',
                data: {
                    expression: expression
                }
            };
            return HttpService.doRequest(settings);
        }

        function createQualification(data) {
            var settings = {
                url: '/api/qualification/',
                method: 'POST',
                data: data
            };
            return HttpService.doRequest(settings);
        }

        function getQualificationItems(qualification_id) {
            var settings = {
                url: '/api/qualification-item/?qualification=' + qualification_id,
                method: 'GET'
            };
            return HttpService.doRequest(settings);
        }

        function openDiscussion(pk) {
            var settings = {
                url: baseUrl + pk + '/discuss/',
                method: 'GET'
            };
            return HttpService.doRequest(settings);
        }

        function getTimeEstimates(pk) {
            var settings = {
                url: baseUrl + pk + '/time-estimate/',
                method: 'GET'
            };
            return HttpService.doRequest(settings);
        }

        function getWorkerDemographics(pk) {
            var settings = {
                url: baseUrl + pk + '/worker-demographics/',
                method: 'GET'
            };
            return HttpService.doRequest(settings);
        }

        function getRemainingCount(pk) {
            var settings = {
                url: baseUrl + pk + '/remaining-tasks/',
                method: 'GET'
            };
            return HttpService.doRequest(settings);
        }

        function getFeedback(pk) {
            var settings = {
                url: baseUrl + pk + '/feedback/',
                method: 'GET'
            };
            return HttpService.doRequest(settings);
        }

        function hasPermission(pk) {
            var settings = {
                url: '/api/task-worker/has-project-permission/?project=' + pk,
                method: 'GET'
            };
            return HttpService.doRequest(settings);
        }

        function postComment(project_id, comment, readyForLaunch) {
            var settings = {
                url: baseUrl + project_id + '/post-comment/',
                method: 'POST',
                data: {
                    comment: {
                        body: comment
                    },
                    ready_for_launch: readyForLaunch
                }
            };
            return HttpService.doRequest(settings);
        }

        function updateComment(pk, comment, readyForLaunch) {
            var settings = {
                url: baseUrl + pk + '/update-comment/',
                method: 'POST',
                data: {
                    comment: {
                        body: comment
                    },
                    ready_for_launch: readyForLaunch
                }
            };
            return HttpService.doRequest(settings);
        }
    }
})();
