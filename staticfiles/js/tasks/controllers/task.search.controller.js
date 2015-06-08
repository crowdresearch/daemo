(function() {
  'use strict';

  angular.module('crowdsource.tasks.controllers', ['smart-table'])
    .factory('Task', Task);
  Task.$inject = ['$http'];

  angular.controller('TaskSearchController', TaskSearchController);

  function TaskSearchController ($scope, $log, Task) {
    var vm = this;

  }
});

