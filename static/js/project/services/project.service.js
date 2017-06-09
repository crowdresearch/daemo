/**
 * Project
 * @namespace crowdsource.project.services
 * @author dmorina neilthemathguy
 */
(function () {
    'use strict';

    angular
        .module('crowdsource.project.services')
        .factory('Project', Project);

    Project.$inject = ['$cookies', '$http', '$q', 'HttpService'];

    /**
     * @namespace Project
     * @returns {Factory}
     */

    function Project($cookies, $http, $q, HttpService) {
        /**
         * @name Project
         * @desc The Factory to be returned
         */

        var Project = {
            retrieve: retrieve,
            getRequesterProjects: getRequesterProjects,
            create: create,
            update: update,
            deleteInstance: deleteInstance,
            attachFile: attachFile,
            deleteFile: deleteFile,
            fork: fork,
            getProjectComments: getProjectComments,
            listWorkerProjects: listWorkerProjects,
            getPreview: getPreview,
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
            recreateTasks: recreateTasks
        };

        return Project;
        /**
         * @name create
         * @desc Create a new Project
         * @returns {Object}
         * @memberOf crowdsource.project.services.Project
         */
        function create() {
            var settings = {
                url: '/api/project/',
                method: 'POST'
            };
            return HttpService.doRequest(settings);
        }

        /**
         * @name update
         * @desc Update an existing project
         * @returns {Object}
         * @memberOf crowdsource.project.services.Project
         */
        function update(pk, data, path) {
            var settings = {
                url: '/api/' + path + '/' + pk + '/',
                method: 'PUT',
                data: data
            };
            return HttpService.doRequest(settings);
        }

        function publish(pk, data) {
            var settings = {
                url: '/api/project/' + pk + '/publish/',
                method: 'POST',
                data: data
            };
            return HttpService.doRequest(settings);
        }

        function updateStatus(pk, data) {
            var settings = {
                url: '/api/project/' + pk + '/update_status/',
                method: 'PUT',
                data: data
            };
            return HttpService.doRequest(settings);
        }

        function recreateTasks(pk, data) {
            var settings = {
                url: '/api/project/' + pk + '/recreate_tasks/',
                method: 'POST',
                data: data
            };
            return HttpService.doRequest(settings);
        }

        function retrieve(pk) {
            var settings = {
                url: '/api/project/' + pk + '/',
                method: 'GET'
            };
            return HttpService.doRequest(settings);
        }

        function retrievePaymentInfo(pk) {
            var settings = {
                url: '/api/project/' + pk + '/payment/',
                method: 'GET'
            };
            return HttpService.doRequest(settings);
        }

        function retrieveSubmittedTasksCount(pk) {
            var settings = {
                url: '/api/project/' + pk + '/submitted-tasks-count/',
                method: 'GET'
            };
            return HttpService.doRequest(settings);
        }

        function lastOpened(pk) {
            var settings = {
                url: '/api/project/' + pk + '/last-opened/',
                method: 'GET'
            };
            return HttpService.doRequest(settings);
        }

        function status(pk) {
            var settings = {
                url: '/api/project/' + pk + '/status/',
                method: 'GET'
            };
            return HttpService.doRequest(settings);
        }

        function get_relaunch_info(pk) {
            var settings = {
                url: '/api/project/' + pk + '/relaunch-info/',
                method: 'GET'
            };
            return HttpService.doRequest(settings);
        }

        function getWorkersToRate(pk) {
            var settings = {
                url: '/api/project/' + pk + '/rate-submissions/',
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
                url: '/api/project/' + pk + '/review-submissions/',
                method: 'GET'
            };
            return HttpService.doRequest(settings);
        }

        function deleteInstance(pk) {
            var settings = {
                url: '/api/project/' + pk + '/',
                method: 'DELETE'
            };
            return HttpService.doRequest(settings);
        }

        function getRequesterProjects() {
            var settings = {
                url: '/api/project/for-requesters/',
                method: 'GET'
            };
            return HttpService.doRequest(settings);
        }


        function attachFile(pk, data) {
            var settings = {
                url: '/api/project/' + pk + '/attach_file/',
                method: 'POST',
                data: data
            };
            return HttpService.doRequest(settings);
        }

        function deleteFile(pk, data) {
            var settings = {
                url: '/api/project/' + pk + '/delete_file/',
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
                url: '/api/project/' + pk + '/fork/',
                method: 'POST'
            };
            return HttpService.doRequest(settings);
        }

        function getProjectComments(pk) {
            var settings = {
                url: '/api/project/' + pk + '/comments/',
                method: 'GET'
            };
            return HttpService.doRequest(settings);
        }

        function listWorkerProjects() {
            var settings = {
                url: '/api/project/for-workers/',
                method: 'GET'
            };
            return HttpService.doRequest(settings);
        }

        function getPreview(pk) {
            var settings = {
                url: '/api/project/' + pk + '/preview/',
                method: 'GET'
            };
            return HttpService.doRequest(settings);
        }

        function createRevision(pk) {
            var settings = {
                url: '/api/project/' + pk + '/create-revision/',
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
                url: '/api/project/' + pk + '/discuss/',
                method: 'GET'
            };
            return HttpService.doRequest(settings);
        }
    }
})();
