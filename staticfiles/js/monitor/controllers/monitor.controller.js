/**
* MonitorController
* @namespace crowdsource.monitor.controllers
 * @author ryosuzuki
*/
(function () {
  'use strict';

  angular
    .module('crowdsource.monitor.controllers')
    .controller('MonitorController', MonitorController);

  MonitorController.$inject = ['$window', '$location', '$scope', 'Monitor', '$filter'];

  /**
  * @namespace MonitorController
  */
  function MonitorController($window, $location, $scope, Monitor, $filter) {
    var vm = $scope;
    vm.workers = [];
    vm.workers = Monitor.getWorkers();
    vm.filter = undefined;
    vm.order = undefined;

    vm.showModal = showModal;
    vm.getPercent = getPercent;
    vm.orderTable = orderTable;
    vm.selectStatus = selectStatus;
    vm.getStatusName = getStatusName;
    vm.getStatusColor = getStatusColor;

    function selectStatus (status) {
      vm.filter = vm.filter !== status ? status : undefined ;
    }

    function orderTable (key) {
      vm.order = vm.order === key ? '-'+key : key;
    }

    function getPercent (workers, status) {
      status |= 0;
      var complete = workers.filter( function (worker) {
        return worker.status == status;
      })
      return Math.floor((complete.length / workers.length) * 100);
    }

    function showModal (worker) {
      vm.selectedWorker = worker;
      $('#myModal').modal();
    }

    function getStatusName (status) {
      return status == 2 ? 'pending' : (status == 1 ? 'in progress' : 'complete');
    }

    function getStatusColor (status) {
      return status == 2 ? 'gray' : (status == 1 ? 'dark' : 'green');
    }
  }
})();