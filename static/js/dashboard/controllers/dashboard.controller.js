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
      self.openTask = openTask;

      activate();
      function activate() {
        Dashboard.getTasksByStatus().then(
          function success(data) {
            self.inProgressTaskWorkers = data[0]['In Progress'];
            self.acceptedTaskWorkers = data[0]['Accepted'];
            self.rejectedTaskWorkers = data[0]['Rejected'];
            self.returnedTaskWorkers = data[0]['Returned'];
          },
          function error(data) {
            $mdToast.showSimple('Could not retrieve your tasks');
          }).finally(function(){}
        );
      }



      function openTask(taskEntry) {
        $location.path('/task/' + taskEntry.task).search('task_worker_id', taskEntry.id);
      }
  }
})();