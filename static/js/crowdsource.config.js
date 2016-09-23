(function () {
    'use strict';

    angular
        .module('crowdsource.config', [])
        .config(config);

    config.$inject = ['$httpProvider', '$locationProvider', '$mdThemingProvider',
        'markedProvider'];

    /**
     * @name config
     * @desc Enable HTML5 routing
     */
    function config($httpProvider, $locationProvider, $mdThemingProvider, markedProvider) {
        $httpProvider.interceptors.push('AuthHttpResponseInterceptor');

        $locationProvider.html5Mode(true);
        $locationProvider.hashPrefix('!');

        markedProvider.setRenderer({
            link: function (href, title, text) {
                return "<a href='" + href + "'" + (title ? " title='" + title + "'" : '') + " target='_blank'>"
                    + text
                    + "</a>";
            }
        });

        // Extend palettes
        var customBlue = $mdThemingProvider.extendPalette('indigo', {
            "50": "#e8e9f2", "100": "#babdd8", "200": "#8d91bf",
            "300": "#666ca9", "400": "#404893", "500": "#3d5987",
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
        var customOrange = $mdThemingProvider.extendPalette('orange', {
            "50": "#fffef3", "100": "#fffbdb", "200": "#fff9c4", "300": "#fff6b0",
            "400": "#fff49c", "500": "#EB7F00", "600": "#dfd477", "700": "#bfb666",
            "800": "#9f9755", "900": "#807944", "A100": "#FFD180", "A200": "#EB7F00",
            "A400": "#FFD180", "A700": "#FFD180"
        });

        // Register the new color palette map with the name <code>neonRed</code>
        $mdThemingProvider.definePalette('customBlue', customBlue);
        $mdThemingProvider.definePalette('customOrange', customOrange);

        $mdThemingProvider.theme('default')
            .primaryPalette('customBlue')
            .accentPalette('customOrange')
            .warnPalette('red')
            .backgroundPalette('grey');

        $mdThemingProvider.setDefaultTheme('default');
    }
})();


