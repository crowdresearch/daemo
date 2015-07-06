(function () {
  'use strict';

  angular
    .module('crowdsource.monitor', [
      'crowdsource.monitor.controllers',
      'crowdsource.monitor.services'
  ]);

  angular
    .module('crowdsource.monitor.controllers', ['angular.filter', 'ngMaterial']);
  angular
    .module('crowdsource.monitor.services', []);

})();