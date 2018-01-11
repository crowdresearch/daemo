(function () {
    'use strict';

    angular
        .module('crowdsource.web-hooks.services')
        .factory('WebHook', WebHook);

    WebHook.$inject = ['$cookies', '$http', '$q', '$sce', 'HttpService'];


    function WebHook($cookies, $http, $q, $sce, HttpService) {
        var baseUrl = HttpService.apiPrefix + '/web-hooks/';
        return {
            create: create,
            update: update,
            delete: deleteInstance,
            retrieve: retrieve,
            list: list
        };

        function create(data) {
            var settings = {
                url: baseUrl,
                method: 'POST',
                data: data
            };
            return HttpService.doRequest(settings);
        }

        function update(pk, data) {
            var settings = {
                url: baseUrl + pk + '/',
                method: 'PUT',
                data: data
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

        function retrieve(pk) {
            var settings = {
                url: baseUrl + pk + '/',
                method: 'GET'
            };
            return HttpService.doRequest(settings);
        }

        function list() {
            var settings = {
                url: baseUrl,
                method: 'GET'
            };
            return HttpService.doRequest(settings);
        }

    }
})();
