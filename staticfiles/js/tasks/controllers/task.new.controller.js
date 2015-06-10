(function() {
  'use strict';

  angular.module('crowdsource.tasks.controllers', ['smart-table'])
    .factory('Task', Task);
  Task.$inject = ['$http'];

  angular.controller('TaskNewController', TaskNewController);

  function TaskNewController ($scope, $log, Task) {
    var vm = this;

  }
});

