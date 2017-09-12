(function () {
    'use strict';

    angular
        .module('crowdsource.task-worker.services')
        .factory('TaskWorker', TaskWorker);

    TaskWorker.$inject = ['HttpService'];


    function TaskWorker(HttpService) {
        var baseUrl = HttpService.apiPrefix + '/assignments/';
        return {
            attemptAllocateTask: attemptAllocateTask,
            getTaskWorker: getTaskWorker
        };


        function attemptAllocateTask(project_id) {
            var settings = {
                url: baseUrl,
                method: 'POST',
                data: {
                    project: project_id
                }
            };
            return HttpService.doRequest(settings);
        }

        function getTaskWorker(pk) {
            var settings = {
                url: baseUrl + pk + '/retrieve-with-data/',
                method: 'GET'
            };
            return HttpService.doRequest(settings);
        }


    }
})();
