/**
 * User
 * @namespace crowdsource.user.services
 */
(function () {
    'use strict';

    angular
        .module('crowdsource.user.services')
        .factory('User', User);

    User.$inject = ['$http', 'HttpService'];


    function User($http, HttpService) {
        var baseUrl = HttpService.apiPrefix + '/users/';
        return {
            getProfile: getProfile,
            getPublicProfile: getPublicProfile,
            updateProfile: updateProfile,
            getCountries: getCountries,
            getPreferences: getPreferences,
            getCities: getCities,
            getJobTitles: getJobTitles,
            listUsernames: listUsernames,
            updatePreferences: updatePreferences,
            setOnline: setOnline,
            create_or_update_aws: create_or_update_aws,
            get_aws_account: get_aws_account,
            removeAWSAccount: removeAWSAccount,
            listWorkers: listWorkers,
            retrieveRequesterBlackList: retrieveRequesterBlackList,
            retrieveRequesterListEntries: retrieveRequesterListEntries,
            createRequesterBlackList: createRequesterBlackList,
            deleteRequesterListEntry: deleteRequesterListEntry,
            createRequesterListEntry: createRequesterListEntry,
            createGroupWithMembers: createGroupWithMembers,
            listFavoriteGroups: listFavoriteGroups,
            getClients: getClients,
            getToken: getToken,
            isProfileComplete: isProfileComplete,
            updatePaymentInfo: updatePaymentInfo,
            getFinancialData: getFinancialData,
            updateCreditCard: updateCreditCard,
            updateBankInfo: updateBankInfo,
            getNotifications: getNotifications,
            isHandleUnique: isHandleUnique,
            updateHandle: updateHandle,
            getAvailableWorkerCount: getAvailableWorkerCount,
            isWhitelisted: isWhitelisted
        };


        function getProfile(username) {
            var settings = {
                url: '/api/profile/',
                method: 'GET'
            };
            return HttpService.doRequest(settings);
        }

        function getPublicProfile(handle) {
            var settings = {
                url: '/api/profile/' + handle + '/public/',
                method: 'GET'
            };
            return HttpService.doRequest(settings);
        }

        function isHandleUnique(handle) {
            var settings = {
                url: '/api/profile/is-handle-unique/?handle=' + handle,
                method: 'GET'
            };
            return HttpService.doRequest(settings);
        }

        function getNotifications() {
            var settings = {
                url: '/api/user/notifications/',
                method: 'GET'
            };
            return HttpService.doRequest(settings);
        }

        function getFinancialData() {
            var settings = {
                url: '/api/profile/financial/',
                method: 'GET'
            };
            return HttpService.doRequest(settings);
        }

        //default-credit-card

        function updateCreditCard(data) {
            var settings = {
                url: '/api/profile/default-credit-card/',
                method: 'PUT',
                data: data
            };
            return HttpService.doRequest(settings);
        }

        function updateBankInfo(data) {
            var settings = {
                url: '/api/profile/default-bank/',
                method: 'PUT',
                data: data
            };
            return HttpService.doRequest(settings);
        }

        function updateProfile(username, data) {
            var settings = {
                url: '/api/profile/' + username + '/',
                method: 'PUT',
                data: JSON.stringify(data)
            };
            return HttpService.doRequest(settings);
        }

        function updateHandle(handle) {
            var settings = {
                url: '/api/profile/update-handle/',
                method: 'PUT',
                data: {
                    handle: handle
                }
            };
            return HttpService.doRequest(settings);
        }

        function getCountries() {
            var settings = {
                url: "/api/country/",
                method: 'GET'
            };
            return HttpService.doRequest(settings);
        }

        function getCities() {
            var settings = {
                url: "/api/city/",
                method: 'GET'
            };
            return HttpService.doRequest(settings);
        }

        function getJobTitles() {
            return $http.get('/static/js/user/data/job_titles.json');
        }

        function listUsernames(pattern) {
            var settings = {
                url: '/api/user/list-username/?pattern=' + pattern,
                method: 'GET'
            };
            return HttpService.doRequest(settings);
        }

        function updatePreferences(username, data) {
            var settings = {
                url: '/api/preferences/' + username + '/',
                method: 'PUT',
                data: data
            };
            return HttpService.doRequest(settings);
        }

        function getPreferences() {
            var settings = {
                url: '/api/preferences/',
                method: 'GET'
            };
            return HttpService.doRequest(settings);
        }

        function setOnline() {
            var settings = {
                url: '/api/user/online/',
                method: 'POST'
            };
            return HttpService.doRequest(settings);
        }

        function create_or_update_aws(data) {
            var settings = {
                url: '/api/mturk-account',
                method: 'POST',
                data: data
            };
            return HttpService.doRequest(settings);
        }

        function get_aws_account() {
            var settings = {
                url: '/api/mturk-account',
                method: 'GET'
            };
            return HttpService.doRequest(settings);
        }

        function removeAWSAccount() {
            var settings = {
                url: '/api/mturk-account/remove',
                method: 'DELETE'
            };
            return HttpService.doRequest(settings);
        }

        function getAccessList(type) {

        }

        function isProfileComplete() {
            var settings = {
                url: '/api/profile/is-complete/',
                method: 'GET'
            };
            return HttpService.doRequest(settings);
        }

        function listWorkers(pattern) {
            var settings = {
                url: '/api/user/list-username/?pattern=' + pattern,
                method: 'GET'
            };
            return HttpService.doRequest(settings);
        }

        function retrieveRequesterBlackList() {
            var settings = {
                url: '/api/requester-access-group/retrieve-global/',
                method: 'GET'
            };
            return HttpService.doRequest(settings);
        }

        function retrieveRequesterListEntries(group) {
            var settings = {
                url: '/api/worker-access-entry/list-by-group/?group=' + group,
                method: 'GET'
            };
            return HttpService.doRequest(settings);
        }

        function createRequesterBlackList() {
            var settings = {
                url: '/api/requester-access-group/',
                method: 'POST',
                data: {
                    "name": "Global blacklist",
                    "type": 2,
                    "is_global": true
                }
            };
            return HttpService.doRequest(settings);
        }

        function createGroupWithMembers(data) {
            var settings = {
                url: '/api/requester-access-group/create-with-entries/',
                method: 'POST',
                data: data
            };
            return HttpService.doRequest(settings);
        }

        function deleteRequesterListEntry(entry_id) {
            var settings = {
                url: '/api/worker-access-entry/' + entry_id + '/',
                method: 'DELETE'
            };
            return HttpService.doRequest(settings);
        }

        function createRequesterListEntry(data) {
            var settings = {
                url: '/api/worker-access-entry/',
                method: 'POST',
                data: data
            };
            return HttpService.doRequest(settings);
        }

        function listFavoriteGroups() {
            var settings = {
                url: '/api/requester-access-group/list-favorites/',
                method: 'GET'
            };
            return HttpService.doRequest(settings);
        }

        function getClients(data) {
            var settings = {
                url: '/api/user/authenticate/',
                method: 'POST',
                data: data
            };
            return HttpService.doRequest(settings);
        }

        function getToken(data) {
            var settings = {
                url: '/api/oauth2-ng/token/',
                method: 'POST',
                data: data
            };
            return HttpService.doRequest(settings);
        }

        function updatePaymentInfo(data) {
            var settings = {
                url: '/api/profile/stripe/',
                method: 'POST',
                data: data
            };
            return HttpService.doRequest(settings);
        }

        function getAvailableWorkerCount() {
            var settings = {
                url: '/api/user/available-workers/',
                method: 'GET'
            };
            return HttpService.doRequest(settings);
        }

        function isWhitelisted() {
            var settings = {
                url: '/api/user/is-whitelisted/',
                method: 'GET'
            };
            return HttpService.doRequest(settings);
        }

    }

})();
