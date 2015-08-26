/**
* Drive
* @namespace crowdsource.dashboard.services
*/
(function () {
  'use strict';

  angular
    .module('crowdsource.dashboard.services')
    .factory('Dashboard', Dashboard);

  Dashboard.$inject = ['$cookies', '$http', '$q', '$location', 'HttpService'];

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
      getTasksByStatus: getTasksByStatus,
      dropSavedTasks: dropSavedTasks
    };
    return Dashboard;

    function getTasksByStatus() {
      var settings = {
        url: '/api/task-worker/list_by_status/',
        method: 'GET'
      };
      return HttpService.doRequest(settings);
    }

    function dropSavedTasks(data) {
      var settings = {
        url: '/api/task-worker/drop_saved_tasks/',
        method: 'POST',
        data: data
      };
      return HttpService.doRequest(settings);
    }
  }
})();
