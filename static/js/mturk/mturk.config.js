(function () {
    'use strict';

    angular
        .module('mturk.config', [])
        .config(config);

    config.$inject = ['$httpProvider', '$locationProvider', '$mdThemingProvider'];

    /**
     * @name config
     * @desc Enable HTML5 routing
     */
    function config($httpProvider, $locationProvider, $mdThemingProvider) {

        $locationProvider.html5Mode(true);
        $locationProvider.hashPrefix('!');

        $mdThemingProvider.theme('default')
            .primaryPalette('deep-purple')
            .accentPalette('light-blue')
            .warnPalette('red')
            .backgroundPalette('grey');
        $mdThemingProvider.setDefaultTheme('default');
    }
})();
