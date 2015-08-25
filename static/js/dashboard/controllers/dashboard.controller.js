/**
* Dashboard controller
* @namespace crowdsource.dashboard.controllers
*/
(function () {
  'use strict';

  angular
    .module('crowdsource.dashboard.controllers')
    .controller('DashboardController', DashboardController);

  DashboardController.$inject = ['$window', '$location', '$scope', '$mdToast', 'Dashboard', '$filter', '$routeParams'];

  /**
  * @namespace DashboardController
  */
  function DashboardController($window, $location, $scope, $mdToast, Dashboard, $filter, $routeParams) {
      var self = this;
      self.getTasksByStatus = getTasksByStatus;

      //Just a simple example of how to get all tasks that are currently in progress
      //status=1 is in progress status=3 is accepted
      getTasksByStatus(1);
      function getTasksByStatus(task_status) {
        Dashboard.getTasksByStatus(task_status).then(
          function success(data, status) {
            console.log(data[0]);
          },
          function error(data,status) {
            console.log("query failed");
          }).finally(function(){}
        );
      }


  }
})();