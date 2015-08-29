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
      self.toggleAll = toggleAll;
      self.toggle = toggle;
      self.isSelected = isSelected;
      self.selectedItems = [];
      self.getSavedTask = getSavedTask;
      self.dropSavedTasks = dropSavedTasks;

      //Just a simple example of how to get all tasks that are currently in progress
      //TODO display data in table

      function toggleAll() {
        if(!self.selectedItems.length) { 
          angular.forEach(self.inProgressTaskWorkers, function(obj) {
            self.selectedItems.push(obj);
          });
          self.selectAll = true;
        } else {
          self.selectedItems = [];
          self.selectAll = false;
        }
      }

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
          function success(data) {
            self.inProgressTaskWorkers = data[0]['In Progress'];
            self.acceptedTaskWorkers = data[0]['Accepted'];
            self.rejectedTaskWorkers = data[0]['Rejected'];
            self.returnedTaskWorkers = data[0]['Returned'];
            processAccepted();
          },
          function error(data) {
            $mdToast.showSimple('Could not retrieve dashboard.')
          }).finally(function(){}
        );
      }

      function processAccepted() {
        self.acceptedModules = {};
        for(var i = 0; i < self.acceptedTaskWorkers.length; i++) {
          var module_id = self.acceptedTaskWorkers[i].module.id;
          if(module_id in self.acceptedModules) {
            self.acceptedModules[module_id].tasks_completed += 1;
          } else {
            self.acceptedModules[module_id] = {
              project: self.acceptedTaskWorkers[i].project_name,
              name: self.acceptedTaskWorkers[i].module.name,
              price: self.acceptedTaskWorkers[i].module.price,
              requester_alias: self.acceptedTaskWorkers[i].requester_alias,
              tasks_completed: 1,
              //assumes we pay all taskworkers at the same time which we will do for microsoft
              is_paid: self.acceptedTaskWorkers[i].is_paid ? 'yes': 'not yet'
            }
          }
        }
        self.totalEarned = 0;
        angular.forEach(self.acceptedModules, function(obj) {
          if(obj.is_paid === "yes") self.totalEarned += obj.price * obj.tasks_completed;
        });
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
                self.selectAll = false;
                activate();
            },
            function error(response) {
              $mdToast.showSimple('Drop tasks failed.')
            }
        ).finally(function () {});
    }
  }
})();