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
      getWorkers: getWorkers
    };

    return Monitor;

    /**
    * @name addMonitor
    * @desc Try to create a new monitor
    * @returns {Promise}
    * @memberOf crowdsource.monitor.services.Monitor
    */
    function getWorkers(id) {
      /*
      return $http({
        url: '/api/monitor/',
        method: 'GET',
        data: {
          id: id,
        }
      });
      */
      return [
        { name: 'A', status: 0, start: '2015-06-08', end: '2015-06-30'},
        { name: 'A', status: 1, start: '2015-06-08', end: '2015-06-30'},
        { name: 'A', status: 0, start: '2015-06-08', end: '2015-06-30'},
        { name: 'A', status: 2, start: '2015-06-08', end: '2015-06-30'},
        { name: 'A', status: 2, start: '2015-06-08', end: '2015-06-30'},
        { name: 'A', status: 1, start: '2015-06-08', end: '2015-06-30'},
        { name: 'A', status: 0, start: '2015-06-08', end: '2015-06-30'},
      ]
    }

  }
})();