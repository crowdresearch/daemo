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
        { name: 'Ryo', status: 0, start: '2015-06-08', time: 10},
        { name: 'Michael', status: 1, start: '2015-06-08', time: 33},
        { name: 'Geza', status: 0, start: '2015-06-08', time: 57},
        { name: 'Rajan', status: 2, start: '2015-06-08', time: 0},
        { name: 'Neil', status: 2, start: '2015-06-08', time: 4},
        { name: 'Joy', status: 1, start: '2015-06-08', time: 26},
        { name: 'Niloufar', status: 0, start: '2015-06-08', time: 48},
        { name: 'Chimay', status: 0, start: '2015-06-08', time: 10},
        { name: 'Kaz', status: 1, start: '2015-06-08', time: 33},
        { name: 'Ethan', status: 0, start: '2015-06-08', time: 57},
        { name: 'Justin', status: 1, start: '2015-06-08', time: 0},
        { name: 'Alexandra', status: 2, start: '2015-06-08', time: 4},
        { name: 'Ranjay', status: 1, start: '2015-06-08', time: 26},
        { name: 'Niloufar', status: 0, start: '2015-06-08', time: 48},
      ]
    }

  }
})();