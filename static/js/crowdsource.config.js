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

        // Extend palettes
        var customBlue = $mdThemingProvider.extendPalette('indigo', {
            "50":"#e8e9f2","100":"#babdd8","200":"#8d91bf",
            "300":"#666ca9","400":"#404893","500":"#1a237e",
            "600":"#171f6e","700":"#141a5f","800":"#10164f",
            "900":"#0d123f","A100":"#babdd8","A200":"#8d91bf",
            "A400":"#404893","A700":"#141a5f"
        });

        var customYellow = $mdThemingProvider.extendPalette('yellow', {
            "50": "#fffef3", "100": "#fffbdb", "200": "#fff9c4", "300": "#fff6b0",
            "400": "#fff49c", "500": "#fff288", "600": "#dfd477", "700": "#bfb666",
            "800": "#9f9755", "900": "#807944", "A100": "#fffbdb", "A200": "#fff9c4",
            "A400": "#fff49c", "A700": "#bfb666"
        });

        var customGrey = $mdThemingProvider.extendPalette('grey', {
            "50":"#ffffff","100":"#ffffff","200":"#ffffff",
            "300":"#ffffff","400":"#ffffff","500":"#ffffff",
            "600":"#dfdfdf","700":"#bfbfbf","800":"#9f9f9f",
            "900":"#808080","A100":"#ffffff","A200":"#ffffff",
            "A400":"#ffffff","A700":"#bfbfbf"
        });

        // Register the new color palette map with the name <code>neonRed</code>
        $mdThemingProvider.definePalette('customBlue', customBlue);
        $mdThemingProvider.definePalette('customYellow', customYellow);
        $mdThemingProvider.definePalette('customGrey', customGrey);

        $mdThemingProvider.theme('default')
            .primaryPalette('customBlue')
            .accentPalette('customYellow')
            .warnPalette('red')
            .backgroundPalette('customGrey');

        $mdThemingProvider.theme('alternate')
            .primaryPalette('indigo')
            .accentPalette('orange')
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