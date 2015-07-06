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

  MonitorController.$inject = ['$window', '$location', '$scope', '$mdSidenav', '$mdUtil', 'Monitor', '$filter'];

  /**
  * @namespace MonitorController
  */
  function MonitorController($window, $location, $scope, $mdSidenav,  $mdUtil, Monitor, $filter) {
    var vm = $scope;
    vm.workers = [];
    Monitor.getTaskWorkerResults().then(function(data) {
      vm.workers = data[0];
    });
    vm.filter = undefined;
    vm.order = undefined;

    vm.showModal = showModal;
    vm.getPercent = getPercent;
    vm.orderTable = orderTable;
    vm.selectStatus = selectStatus;
    vm.getStatusName = getStatusName;
    vm.getStatusColor = getStatusColor;
    vm.getAction = getAction;

    vm.toggleRight = toggleRight();

    function toggleRight (worker) {
      vm.worker = worker
      var debounceFn =  $mdUtil.debounce(function(){
        $mdSidenav('right')
        .toggle()
      },30);
      return debounceFn;
    }

    vm.close = function () {
      $mdSidenav('right').close();
    };

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
      });
      return Math.floor((complete.length / workers.length) * 100);
    }

    function showModal (worker) {
      vm.selectedWorker = worker;
      $('#myModal').modal();
    }

    function getStatusName (status) {
      return status == 1 ? 'in progress' : (status == 2 ? 'submitted' : (status == 3 ? 'approved' : 'rejected'));
    }

    function getStatusColor (status) {
      return status == 3 ? 'gray' : (status == 2 ? 'dark' : 'green');
    }

    function getAction (status) {
      return status == 2;
    }
  }
})();