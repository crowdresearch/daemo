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

  TaskFeedController.$inject = ['$window', '$location', '$scope', 'TaskFeed', '$filter'];

  /**
  * @namespace TaskFeedController
  */
  function TaskFeedController($window, $location, $scope, TaskFeed, $filter) {
      var self = this;
  }
})();