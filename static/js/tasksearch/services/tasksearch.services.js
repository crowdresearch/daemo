/**
* TaskSearchService
* @namespace crowdsource.tasksearch.services
*/
(function () {
  'use strict';

  angular
    .module('crowdsource.tasksearch.services')
    .factory('TaskSearchService', TaskSearchService);

  TaskSearchService.$inject = ['$cookies', '$q', '$location', 'HttpService'];

  /**
  * @namespace TaskService
  * @returns {Factory}
  */

  function TaskSearchService($cookies, $q, $location, HttpService) {
    /**
    * @name TaskSearchService
    * @desc The Factory to be returned
    */
    var TaskSearchService = {
      getModule: getModule
    };

    return TaskSearchService;


    /**
    * @name getModule
    * @desc Get module.
    * @returns {Promise}
    * @memberOf crowdsource.tasksearch.services.TaskSearchService
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