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
        clientId: '4PcTMZt8BvCLFVA8nSnp6UtZa87wfXwCjGqDhSbt',
        clientSecret: 'zT3rCTIGlVaHCvfuLYVaSrrA8MDIPPkrKVLFRn3zgPVegn8iHe5SnkypECbjyADEiCwAEnlXQcDVcDVG72iuyHLOVpUy8z30XdaYBr5mj80Uw4vw060d2ZWxcKls9QSs',
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