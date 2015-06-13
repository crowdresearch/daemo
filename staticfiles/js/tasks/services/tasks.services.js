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
      getModule: getModule
    };

    return TaskService;


    /**
    * @name getModule
    * @desc Get module.
    * @returns {Promise}
    * @memberOf crowdsource.tasks.services.TaskService
    */
    function getModule() {
      var settings = {
        url: "/api/module/?format=json",
        method: 'GET'
      };
      return HttpService.doRequest(settings);
    }

  }
})();