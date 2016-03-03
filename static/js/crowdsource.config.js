(function () {
    'use strict';

    angular
        .module('crowdsource.config', ['angular-loading-bar'])
        .config(config);

    config.$inject = ['$httpProvider', '$locationProvider', '$mdThemingProvider'];

    /**
     * @name config
     * @desc Enable HTML5 routing
     */
    function config($httpProvider, $locationProvider, $mdThemingProvider) {
        $httpProvider.interceptors.push('AuthHttpResponseInterceptor');

        $locationProvider.html5Mode(true);
        //$locationProvider.hashPrefix('!');

        // Extend palettes
        var customBlue = $mdThemingProvider.extendPalette('indigo', {
            "50": "#e8e9f2", "100": "#babdd8", "200": "#8d91bf",
            "300": "#666ca9", "400": "#404893", "500": "#1a237e",
            "600": "#171f6e", "700": "#141a5f", "800": "#10164f",
            "900": "#0d123f", "A100": "#babdd8", "A200": "#8d91bf",
            "A400": "#404893", "A700": "#141a5f"
        });

        var customYellow = $mdThemingProvider.extendPalette('yellow', {
            "50": "#fffef3", "100": "#fffbdb", "200": "#fff9c4", "300": "#fff6b0",
            "400": "#fff49c", "500": "#fff288", "600": "#dfd477", "700": "#bfb666",
            "800": "#9f9755", "900": "#807944", "A100": "#fffbdb", "A200": "#fff9c4",
            "A400": "#fff49c", "A700": "#bfb666"
        });

        // Register the new color palette map with the name <code>neonRed</code>
        $mdThemingProvider.definePalette('customBlue', customBlue);
        $mdThemingProvider.definePalette('customYellow', customYellow);

        $mdThemingProvider.theme('default')
            .primaryPalette('deep-purple')
            .accentPalette('light-blue')
            .warnPalette('red')
            .backgroundPalette('grey');

        $mdThemingProvider.setDefaultTheme('default');
    }
})();
