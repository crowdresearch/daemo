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
      getTaskWorkerResults: getTaskWorkerResults,
      updateResultStatus: updateResultStatus
    };

    return Monitor;

    function getTaskWorkerResults(){
      var settings = {
        url: '/api/task-worker-result/',
        method: 'GET',
      };
      return HttpService.doRequest(settings);
    }

    function updateResultStatus(twr){
      var settings = {
        url: '/api/task-worker-result/' + twr.id + '/',
        method: 'PUT',
        data: twr
      };
      return HttpService.doRequest(settings);
    }

  }
  
})();