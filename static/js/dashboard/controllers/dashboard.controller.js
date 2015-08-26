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
      self.toggle = toggle;
      self.isSelected = isSelected;
      self.selectedItems = [];
      self.getSavedTask = getSavedTask;
      self.dropSavedTasks = dropSavedTasks;

      //Just a simple example of how to get all tasks that are currently in progress
      //TODO display data in table

      function toggle(item) {
          var idx = self.selectedItems.indexOf(item);
          if (idx > -1) self.selectedItems.splice(idx, 1);
          else self.selectedItems.push(item);
      }
      function isSelected(item){
          return !(self.selectedItems.indexOf(item) < 0);
      }

      activate();
      function activate() {
        Dashboard.getTasksByStatus().then(
          function success(data, status) {
            self.inProgressTaskWorkers = data[0]['In Progress'];
            self.acceptedTaskWorkers = data[0]['Accepted'];
            self.rejectedTaskWorkers = data[0]['Rejected'];
            self.returnedTaskWorkers = data[0]['Returned'];
          },
          function error(data,status) {
            console.log("query failed");
          }).finally(function(){}
        );
      }

      //TODO process data as html upon click of inprogress task and allow worker to finish/delete task
      //Reroute to task feed or just stay in dashboard???
      function getSavedTask() {
        if(self.selectedItems.length != 1) {
          $mdToast.showSimple('You can only return to 1 task at a time');
          return;
        }
        $location.path('/task/' + self.selectedItems[0].task + '/' + self.selectedItems[0].id);
      }

      function dropSavedTasks() {
        var request_data = {
          task_ids: []
        };
        angular.forEach(self.selectedItems, function(obj) {
            request_data.task_ids.push(obj.task);
        });
        Dashboard.dropSavedTasks(request_data).then(
            function success(response) {
                self.selectedItems = [];
                activate();
            },
            function error(response) {
              $mdToast.showSimple('Drop tasks failed.')
            }
        ).finally(function () {});
    }
  }
})();