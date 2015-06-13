(function () {
  'use strict';

  angular
    .module('crowdsource.authentication', [
      'crowdsource.authentication.controllers',
      'crowdsource.authentication.services'
    ]);

  angular
    .module('crowdsource.authentication.controllers', []);

  angular
    .module('crowdsource.authentication.services', ['ngCookies']);
})();