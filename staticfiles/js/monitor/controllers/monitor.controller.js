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
    vm.getStatusName = getStatusName;
    vm.getStatusColor = getStatusColor;

    function getStatusName (status) {
      return status == 0 ? 'complete' : (status == 1 ? 'in progress' : 'pending');
    }

    function getStatusColor (status) {
      return status == 0 ? 'status-green' : (status == 1 ? 'status-dark' : 'status-gray');
    }
  }
})();