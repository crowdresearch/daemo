(function () {
  'use strict';

  angular
    .module('crowdsource.config', ['angular-loading-bar'])
    .config(config);

  config.$inject = ['$locationProvider', 'cfpLoadingBarProvider'];

  /**
  * @name config
  * @desc Enable HTML5 routing
  */
  function config($locationProvider, cfpLoadingBarProvider) {
    $locationProvider.html5Mode(true);
    $locationProvider.hashPrefix('!');
    cfpLoadingBarProvider.includeSpinner = false;
  }
})();