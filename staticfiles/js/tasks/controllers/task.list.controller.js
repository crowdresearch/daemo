(function() {
  'use strict';

  angular.module('crowdsource.tasks.controllers', ['smart-table'])
    .factory('Task', Task);
  Task.$inject = ['$http'];

  angular.controller('TaskNewController', TaskController);

  function TaskNewController ($scope, $log, Task) {
    var vm = this;

    vm.displayedCollection = [];
    vm.rowCollection = [];

    Task.getList().then( function success (data, config) {
      vm.displayedCollection = data;
      vm.rowCollection = data;
    }, function error (data, status, headers, config) {
      console.log(status);
    })

    vm.gridOptionsTask = {
      multiSelect: false,
      enablePinning: true,
      data:'task',
      columnDefs: [
        { field: "name", displayName: 'Name', width: 200, pinned: true },
        { field: "description", displayName: 'Description', width:150 },
        { field:"keywords",displayName: 'Keywords', width:190 },
        { field: "module_timeout", displayName:'Hours Remain', width:130 },
        { field: "repetition", displayName: 'Repetition', width: 100 },
        { field: "price", displayName: 'Pay', width: 60 },
      ]
    };
  }
});

