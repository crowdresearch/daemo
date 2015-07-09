/**
* TaskService
* @namespace crowdsource.tasks.services
*/
(function () {
  'use strict';

  angular
    .module('crowdsource.tasks.services')
    .factory('TaskService', TaskService);

  TaskService.$inject = ['$cookies', '$q', '$location', 'HttpService'];

  /**
  * @namespace TaskService
  * @returns {Factory}
  */

  function TaskService($cookies, $q, $location, HttpService) {
    /**
    * @name TaskService
    * @desc The Factory to be returned
    */
    var TaskService = {
      getModule: getModule,
      getTask: getTask,
      acceptTask: acceptTask
    };

    return TaskService;

    function getTask(taskId) {
      var settings = {
        url: '/api/task/' + taskId + '/',
        method: 'GET'
      };
      return HttpService.doRequest(settings);
    }

    function acceptTask(module_id) {
      var settings = {
        url: '/api/task-worker/',
        method: 'POST',
        data: {
          module: module_id
        }
      };
      return HttpService.doRequest(settings);
    }

    function getModule (moduleId) {
      var settings = {
        url: '/api/module/' + moduleId + '/',
        method: 'GET'
      };
      return HttpService.doRequest(settings);
    }

  }
})();