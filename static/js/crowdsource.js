angular
    .module('crowdsource', [
        // third party modules
        'angular-loading-bar',
        'ngFx',
        'ngMessages',
        'ngAnimate',
        'ngSanitize',
        'ngMaterial',
        'ngDragDrop',
        'ngFileUpload',
        'ng-sortable',
        'angular-clipboard',
        'ui.router',
        'ngWebsocket',
        // local modules
        'crowdsource.config',
        'crowdsource.interceptor',
        'crowdsource.routes',
        'crowdsource.localstorage',
        'crowdsource.authentication',
        'crowdsource.layout',
        'crowdsource.home',
        'crowdsource.requester',
        'crowdsource.rating',
        'crowdsource.task',
        'crowdsource.directives',
        'crowdsource.services',
        'crowdsource.worker',
        'crowdsource.skill',
        'crowdsource.project',
        'crowdsource.payment',
        'crowdsource.task-feed',
        'crowdsource.task-worker',
        'crowdsource.template',
        'crowdsource.drive',
        'crowdsource.data-table',
        'crowdsource.user',
        'crowdsource.helpers',
        'crowdsource.contributor'
    ]);

angular
    .module('crowdsource')
    .run(run);

run.$inject = ['$http', '$rootScope', '$window', '$location', 'Authentication'];

/**
 * @name run
 * @desc Update xsrf $http headers to align with Django's defaults
 */
function run($http, $rootScope, $window, $location, Authentication) {
    $http.defaults.xsrfHeaderName = 'X-CSRFToken';
    $http.defaults.xsrfCookieName = 'csrftoken';

    //$rootScope.$on('$routeChangeStart', function (event, next) {
    //    var isAuthenticated = Authentication.isAuthenticated();
    //
    //    if (!isAuthenticated && next.hasOwnProperty('$$route') && next.$$route.hasOwnProperty('authenticated') && next.$$route.authenticated) {
    //        event.preventDefault();
    //
    //        $rootScope.isLoggedIn = isAuthenticated;
    //        $rootScope.account = null;
    //
    //        $location.path('/login');
    //    }
    //});

    $rootScope.$on("$stateChangeStart",
        function (event, toState, toParams, fromState, fromParams) {
            var isAuthenticated = Authentication.isAuthenticated();

            if (toState.authenticate && !isAuthenticated) {
                $rootScope.isLoggedIn = isAuthenticated;
                $rootScope.account = null;

                $state.transitionTo('login');

                event.preventDefault();
            }
        });


    $rootScope.theme = 'default';

    $rootScope.getWebsocketUrl = function () {
        var host = $location.host();
        var protocol = $location.protocol();
        var port = $location.port();

        protocol = protocol.replace("http", "ws");

        return protocol + "://" + host + ":" + port;
    };

    /*$rootScope.$on('oauth:error', function(event, rejection) {
     if ('invalid_grant' === rejection.data.error) {
     return;
     }
     if ('invalid_token' === rejection.data.error) {
     return OAuth.getRefreshToken();
     }
     return $window.location.href = '/login?error_reason=' + rejection.data.error;
     });*/
}
