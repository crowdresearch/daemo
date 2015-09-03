(function () {
    'use strict';

    angular
        .module('crowdsource.config', ['angular-loading-bar'])
        .config(config);

    config.$inject = ['$httpProvider', '$locationProvider', '$mdThemingProvider', 'cfpLoadingBarProvider'];

    /**
     * @name config
     * @desc Enable HTML5 routing
     */
    function config($httpProvider, $locationProvider, $mdThemingProvider, cfpLoadingBarProvider) {
        $httpProvider.interceptors.push('AuthHttpResponseInterceptor');

        $locationProvider.html5Mode(true);
        $locationProvider.hashPrefix('!');

        cfpLoadingBarProvider.includeSpinner = false;

        $mdThemingProvider.theme('default')
            .primaryPalette('indigo')
            .accentPalette('pink')
            .warnPalette('red')
            .backgroundPalette('grey');

        $mdThemingProvider.theme('alternate')
            .dark()
            .primaryPalette('orange')
            .accentPalette('green')
            .warnPalette('red')
            .backgroundPalette('grey');

        $mdThemingProvider.setDefaultTheme('default');
//        $mdThemingProvider.alwaysWatchTheme(true);


        //testing
        /*OAuthProvider.configure({
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
         });*/
    }
})();