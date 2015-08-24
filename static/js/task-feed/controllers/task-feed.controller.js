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

  TaskFeedController.$inject = ['$window', '$location', '$scope', '$mdToast', 'TaskFeed',
    '$filter', 'Authentication', 'TaskWorker', 'Project'];

  /**
  * @namespace TaskFeedController
  */
  function TaskFeedController($window, $location, $scope, $mdToast, TaskFeed,
    $filter, Authentication, TaskWorker, Project) {
      var userAccount = Authentication.getAuthenticatedAccount();
      if (!userAccount) {
        $location.path('/login');
        return;
      }
      
      var self = this;
      self.toggleBookmark = toggleBookmark;
      self.projects = [];
      self.previewedModule = null;
      self.showPreview = showPreview;
      self.openTask = openTask;
      self.openComments = openComments;

      TaskFeed.getProjects().then(
        function success (data) {
            self.projects = data[0];
        },
        function error(errData) {
          self.error = errData[0].detail;
          $mdToast.showSimple('Could not get task with data.');
        }
      ).finally(function () {
        // pass
      });

      function toggleBookmark(project){
          project.is_bookmarked = !project.is_bookmarked;
      }
      function showPreview(module){
          self.previewedModule = module;
      }

      function openTask(module_id){
        TaskWorker.attemptAllocateTask(module_id).then(
        function success (data) {
            var task_id = data[0].task;
            $location.path('/task/'+task_id);
        },
        function error(errData) {
          var err = errData[0];
          $mdToast.showSimple('Error attempting task - ' + JSON.stringify(err));
        }
        ).finally(function () {
        });
      }
      function openComments(module_id){
        Project.getModuleComments(module_id).then(
        function success(data) {
            //var task_id = data[0].task;
            console.log(data[0]);
        },
        function error(errData) {
          var err = errData[0];
          $mdToast.showSimple('Error fetching comments - ' + JSON.stringify(err));
        }
        ).finally(function () {
        });
      }
  }

})();