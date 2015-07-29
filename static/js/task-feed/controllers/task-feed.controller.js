/**
* TaskFeedController
* @namespace crowdsource.task-feed.controllers
 * @author dmorina
*/
(function () {
  'use strict';

  angular
    .module('crowdsource.task-feed.controllers')
    .controller('TaskFeedController', TaskFeedController);

  TaskFeedController.$inject = ['$window', '$location', '$scope', 'TaskFeed', '$filter', 'Authentication'];

  /**
  * @namespace TaskFeedController
  */
  function TaskFeedController($window, $location, $scope, TaskFeed, $filter, Authentication) {
      var userAccount = Authentication.getAuthenticatedAccount();
      if (!userAccount) {
        $location.path('/login');
        return;
      }
      
      var self = this;
      self.toggleBookmark = toggleBookmark;
      self.modules = [];

      TaskFeed.getProjects().then(
        function success (data) {
            self.modules = data[0];
          /*
          var data = successData[0];
          self.projects = data;
          var modules = [];
          var moduleTasks = [];
          
          // Get all modules
          data.forEach(function (project) {
            project.modules.forEach(function(module) {
              modules.push(module);
            });
          });
          
          // get all module tasks
          modules.forEach(function (module) {
            module.module_tasks.forEach(function (task) {
              moduleTasks.push(task);
            });
          });

          // Check if module tasks have any worker, if not, they then are free to attempt.
          var freeTasks = {};
          moduleTasks.forEach(function (task) {
            if (task.task_workers.length === 0)
            freeTasks[task.module] = task;
          });

          // Make an array of available modules and their correpsonding tasks map back to freetask.
          var freeModules = [];
          modules.forEach(function (mod) {
            if (freeTasks.hasOwnProperty(mod.id)) {
              freeModules.push(mod);
            }
          });

          self.freeModules = freeModules;
          self.freeTasks = _.toArray(freeTasks);
          //console.log(self.freeModules, self.projects);
          */
        },
        function error(errData) {
          self.error = errData[0].detail;
        }
      ).finally(function () {
        // pass
      });

      function toggleBookmark(project){
          project.is_bookmarked = !project.is_bookmarked;
      }
  }

})();