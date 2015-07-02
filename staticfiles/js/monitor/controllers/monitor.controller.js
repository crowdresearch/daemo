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
    Monitor.getTaskWorkerResults().success(function(data) {
      vm.workers = data;
    });
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
      status |= 1;
      var complete = workers.filter( function (worker) {
        return worker.status == status;
      })
      console.log(complete);
      return Math.floor((complete.length / workers.length) * 100);
    }

    function showModal (worker) {
      vm.selectedWorker = worker;
      $('#myModal').modal();
    }

    function getStatusName (status) {
      return status == 3 ? 'rejected' : (status == 2 ? 'accepted' : 'created');
    }

    function getStatusColor (status) {
      return status == 3 ? 'gray' : (status == 2 ? 'dark' : 'green');
    }
  }
})();