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

        var customBlue = $mdThemingProvider.extendPalette('indigo', {
            "50": "#e8e9f2", "100": "#babdd8", "200": "#8d91bf",
            "300": "#666ca9", "400": "#404893", "500": "#3d5987",
            "600": "#171f6e", "700": "#141a5f", "800": "#10164f",
            "900": "#0d123f", "A100": "#babdd8", "A200": "#8d91bf",
            "A400": "#404893", "A700": "#141a5f"
        });
        $mdThemingProvider.definePalette('customBlue', customBlue);
        $mdThemingProvider.theme('default')
            .primaryPalette('customBlue')
            .accentPalette('light-blue')
            .warnPalette('red')
            .backgroundPalette('grey');
        $mdThemingProvider.setDefaultTheme('default');
    }
})();
