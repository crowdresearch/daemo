(function () {
  'use strict';

  angular
    .module('crowdsource.worker', [
      'crowdsource.worker.controllers',
       'crowdsource.worker.services'
    ]);

  angular
    .module('crowdsource.worker.controllers', []);

  angular
    .module('crowdsource.worker.services', ['ngCookies']);

})();