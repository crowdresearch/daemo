/**
 * Created by dmorina on 16/04/15.
 */
(function () {
  'use strict';
  angular
    .module('crowdresearch.user_management', [
      'crowdresearch.user_management.controllers',
      'crowdresearch.user_management.services'
    ]);

  angular
    .module('crowdresearch.user_management.controllers', []);

  angular
    .module('crowdresearch.user_management.services', ['ngCookies']);
})();