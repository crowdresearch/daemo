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
    vm.workers = Monitor.getWorkers();
  }
})();