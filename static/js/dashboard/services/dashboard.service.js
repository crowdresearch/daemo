/**
* Drive
* @namespace crowdsource.dashboard.services
*/
(function () {
  'use strict';

  angular
    .module('crowdsource.dashboard.services')
    .factory('Dashboard', Dashboard);

  Drive.$inject = ['$cookies', '$http', '$q', '$location', 'HttpService'];

  /**
  * @namespace Dashboard
  * @returns {Factory}
  */

  function Dashboard($cookies, $http, $q, $location, HttpService) {
    /**
    * @name Dashboard
    * @desc The Factory to be returned
    */
    var Dashboard = {
    };
    return Dashboard;

  }
})();
