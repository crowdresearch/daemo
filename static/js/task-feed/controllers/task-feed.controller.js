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
      self.projects = [];
      self.previewedModule = null;
      self.showPreview = showPreview;

      TaskFeed.getProjects().then(
        function success (data) {
            self.projects = data[0];
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
      function showPreview(module){
          self.previewedModule = module;
      }
  }

})();