(function () {
  'use strict';

  angular
    .module('crowdsource.config', ['angular-loading-bar'])
    .config(config);

  config.$inject = ['$locationProvider', 'cfpLoadingBarProvider', 'OAuthProvider','OAuthTokenProvider'];

  /**
  * @name config
  * @desc Enable HTML5 routing
  */
  function config($locationProvider, cfpLoadingBarProvider, OAuthProvider, OAuthTokenProvider) {
    $locationProvider.html5Mode(true);
    $locationProvider.hashPrefix('!');
    cfpLoadingBarProvider.includeSpinner = false;
    //testing
    OAuthProvider.configure({
        baseUrl: 'http://localhost:8000',
        clientId: 'client_id',
        clientSecret: 'client_secret',
        grantPath : '/api/oauth2-ng/token'
    });

    OAuthTokenProvider.configure({
      name: 'token',
      options: {
        secure: false //TODO this has to be changed to True
      }
    });
  }
})();