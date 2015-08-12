/**
* TaskWorkerService
* @namespace crowdsource.task-worker.services
*/
(function () {
  'use strict';

  angular
    .module('crowdsource.task-worker.services')
    .factory('TaskWorker', TaskWorker);

  TaskWorker.$inject = ['$cookies', '$q', '$location', 'HttpService'];

  /**
  * @namespace TaskWorker
  * @returns {Factory}
  */

  function TaskWorker($cookies, $q, $location, HttpService) {
    /**
    * @name TaskWorker
    * @desc The Factory to be returned
    */
    var TaskWorker = {
      getTaskWorker: getTaskWorker,
      submitResult: submitResult,
      attemptAllocateTask: attemptAllocateTask
    };

    return TaskWorker;


    function getTaskWorker(taskWorkerId) {
      var settings = {
        url: '/api/task-worker/' + taskWorkerId + '/',
        method: 'GET'
      };
      return HttpService.doRequest(settings);
    }

    function submitResult(taskWorkerId, results) {
      var settings = {
        url: '/api/task-worker-result/' + taskWorkerId + '/',
        method: 'PUT',
        data: {
          result: results
        }
      };
      return HttpService.doRequest(settings); 
    }

    function attemptAllocateTask(module_id) {
      var settings = {
        url: '/api/task-worker/',
        method: 'POST',
        data: {
          module: module_id
        }
      };
      return HttpService.doRequest(settings);
    }


  }
})();