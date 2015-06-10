(function() {
  'use strict';

  angular.module('crowdsource.tasks.controllers', ['smart-table'])
    .factory('Task', Task);
  Task.$inject = ['$http'];

  angular.controller('TaskShowController', TaskShowController);

  function TaskShowController ($scope, $log, Task) {
    var vm = this;

  }
});

