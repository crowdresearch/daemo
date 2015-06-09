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
      var self = this;
      self.startDate = $filter('date')(new Date(), 'yyyy-MM-dd h:mma Z');
      self.addMonitor = addMonitor;
      self.endDate = null;
      self.name = null;
      self.description = null;
      self.categories = '';

      self.categoryPool = ('Programming Painting Design Image-Labelling Writing')
          .split(' ').map(function (category) { return { name: category }; });
      /**
       * @name addMonitor
       * @desc Create new monitor
       * @memberOf crowdsource.monitor.controllers.MonitorController
       */
      function addMonitor() {
          Monitor.addMonitor(self.name, self.startDate, self.endDate, self.description).then(
            function success(data, status) {
              //TODO
            },
            function error(data, status) {
                self.error = data.data.detail;
                //$scope.form.$setPristine();
          }).finally(function () {

              });
      }
  }
})();