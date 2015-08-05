/**
* Monitor
* @namespace crowdsource.monitor.services
*/
(function () {
  'use strict';

  angular
    .module('crowdsource.monitor.services')
    .factory('Monitor', Monitor);

  Monitor.$inject = ['$http','HttpService'];

  /**
  * @namespace Monitor
  * @returns {Factory}
  */

  function Monitor($http, HttpService) {
    /**
    * @name Monitor
    * @desc The Factory to be returned
    */
    var Monitor = {
      getProject: getProject,
      getRequesterTaskWorkerResults: getRequesterTaskWorkerResults,
      updateResultStatus: updateResultStatus
    };

    return Monitor;

    function getProject(projectId) {
      var settings = {
        url: 'api/project/' + projectId + '/',
        method: 'GET'
      };
      return HttpService.doRequest(settings);
    }


    function getRequesterTaskWorkerResults(module_id){
      var settings = {
        url: '/api/task-worker-result/requester_taskworkerresults/',
        method: 'POST',
        data: {
          module_id: module_id
        }
      };
      return HttpService.doRequest(settings);
    }

    function updateResultStatus(twr){
      console.log(twr);
      var settings = {
        url: '/api/task-worker-result/' + twr.id + '/',
        method: 'PUT',
        data: twr
      };
      return HttpService.doRequest(settings);
    }

  }
  
})();