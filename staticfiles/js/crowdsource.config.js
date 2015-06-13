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
        clientId: 'XtO3np9W7YcyKW0wAu2LF8iyaRjblj8eWLuLOLeY',
        clientSecret: 'QtWCBDmEcZML2motrtsII0gaD0hQJ0DdrfFv01Z3tnrlUJoW4Ev1uAHJH0v9UAlzQOkFiHFYsiUBjU15rNwxxDKeuu0gNH20mr4EOZGSXfZxPbEzFC4r3hzi2XdsGlw6',
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