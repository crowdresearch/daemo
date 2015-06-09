/**
* Monitor
* @namespace crowdsource.monitor.services
*/
(function () {
  'use strict';

  angular
    .module('crowdsource.monitor.services')
    .factory('Monitor', Monitor);

  Monitor.$inject = ['$cookies', '$http', '$q', '$location'];

  /**
  * @namespace Monitor
  * @returns {Factory}
  */

  function Monitor($cookies, $http, $q, $location) {
    /**
    * @name Monitor
    * @desc The Factory to be returned
    */
    var Monitor = {
      addMonitor: addMonitor
    };

    return Monitor;


    /**
    * @name addMonitor
    * @desc Try to create a new monitor
    * @returns {Promise}
    * @memberOf crowdsource.monitor.services.Monitor
    */
    function addMonitor(name, startDate, endDate, description) {
      return $http({
        url: '/api/monitor/',
        method: 'POST',
        data: {
          name: name,
          start_date: startDate,
          end_date: endDate,
          description: description
        }
      });
    }

  }
})();