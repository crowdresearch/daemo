/**
* Monitor
* @namespace crowdsource.monitor.services
*/
(function () {
  'use strict';

  angular
    .module('crowdsource.monitor.services')
    .factory('Monitor', Monitor);

  Monitor.$inject = ['$http'];

  /**
  * @namespace Monitor
  * @returns {Factory}
  */

  function Monitor($http) {
    /**
    * @name Monitor
    * @desc The Factory to be returned
    */
    var Monitor = {
      getTaskWorkerResults: getTaskWorkerResults
    };

    return Monitor;

    function getTaskWorkerResults(){
      return $http({
        url: '/api/task-worker-result/',
        method: 'GET'
      });
    }
  }
  
})();