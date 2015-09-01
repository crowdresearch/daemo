/**
* Dashboard controller
* @namespace crowdsource.dashboard.controllers
*/
(function () {
  'use strict';

  angular
    .module('crowdsource.dashboard.controllers')
    .controller('DashboardController', DashboardController);

  DashboardController.$inject = ['$window', '$location', '$scope', '$mdToast', 'Dashboard', '$filter', '$routeParams', 'RankingService'];

  /**
  * @namespace DashboardController
  */
  function DashboardController($window, $location, $scope, $mdToast, Dashboard, $filter, $routeParams, RankingService) {
      var self = this;
      self.toggleAll = toggleAll;
      self.toggle = toggle;
      self.isSelected = isSelected;
      self.selectedItems = [];
      self.getSavedQueue = getSavedQueue;
      self.dropSavedTasks = dropSavedTasks;

//      getWorkerData();
      getRequesterData();

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
            self.submittedTaskWorkers = data[0]['Submitted'];
            //Eventually I think we will probably want to do this processing on the backend
            processAccepted();
            processSubmitted();
          },
          function error(data) {
            $mdToast.showSimple('Could not retrieve dashboard.')
          }).finally(function(){}
        );
      }

      function processSubmitted() {
        self.submittedModules = {};
        for(var i = 0; i < self.submittedTaskWorkers.length; i++) {
          var module_id = self.submittedTaskWorkers[i].module.id;
          if(module_id in self.submittedModules) {
            self.submittedModules[module_id].tasks_completed += 1;
            if(self.submittedModules[module_id].last_submission < self.submittedTaskWorkers[i].last_updated) {
              self.submittedModules[module_id].last_submission = self.submittedTaskWorkers[i].last_updated;
            }
          } else {
            self.submittedModules[module_id] = {
              project: self.submittedTaskWorkers[i].project_name,
              name: self.submittedTaskWorkers[i].module.name,
              price: self.submittedTaskWorkers[i].module.price,
              requester_alias: self.submittedTaskWorkers[i].requester_alias,
              tasks_completed: 1,
              last_submission: self.submittedTaskWorkers[i].last_updated
            }
          }
        }
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
        for(var i=0; i < self.requesterRankings.length; i++) {

        }
        self.totalEarned = 0;
        angular.forEach(self.acceptedModules, function(obj) {
          if(obj.is_paid === "yes") self.totalEarned += obj.price * obj.tasks_completed;
        });
      }

      function getSavedQueue() {
        Dashboard.savedQueue = self.selectedItems;
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

    function getWorkerData() {
      self.pendingRankings = [];
      RankingService.getWorkerRankings().then(
        function success (resp) {
          var data = resp[0];
          data = data.map(function (item) {
            item.reviewType = 'requester';
            return item;
          });
          self.pendingRankings = data;
        },
        function error (errResp) {
          var data = resp[0];
          $mdToast.showSimple('Could not get worker rankings.');
        });
    }

    function getRequesterData() {
      self.requesterRankings = [];
      RankingService.getRequesterRankings().then(
        function success (resp) {
          var data = resp[0];
          data = data.map(function (item) {
            item.reviewType = 'worker';
            return item;
          });
          self.requesterRankings = data;
        },
        function error (errResp) {
          var data = resp[0];
          $mdToast.showSimple('Could not get requester rankings.');
        });
    }

    function refreshData(reviewType) {
      if (reviewType === 'requester') {
        getWorkerData();
      } else {
        getRequesterData();
      }
    }

    // TODO figure out a better way to handle data refresh.
    self.handleRatingSubmit = function (rating, entry) {
      entry.current_rating = rating;
      if (entry.current_rating_id) {
        RankingService.updateRating(rating, entry).then(function success(resp) {
        }, function error (resp) {
          $mdToast.showSimple('Could not update rating.');
        }).finally(function () {
          refreshData(entry.reviewType);
        });
      } else {
        RankingService.submitRating(rating, entry).then(function success(resp) {
        }, function error (resp) {
          $mdToast.showSimple('Could not submit rating.')
        }).finally(function () {
          refreshData(entry.reviewType);
        });
      }

    }
  }
})();