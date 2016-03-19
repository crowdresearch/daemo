angular
    .module('crowdsource', [
        // third party modules
        'angular-loading-bar',
        'ngFx',
        'ngMessages',
        'ngAnimate',
        'ngSanitize',
        'ngMaterial',
        'ngFileUpload',
        'ng-sortable',
        'ui.router',
        'ngWebsocket',

        // local modules
        'crowdsource.config',
        'crowdsource.interceptor',
        'crowdsource.routes',
        'crowdsource.localstorage',
        'crowdsource.authentication',
        'crowdsource.layout',
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
        'crowdsource.contributor',
        'crowdsource.message'
    ]);

angular
    .module('crowdsource')
    .run(run);

run.$inject = ['$http', '$rootScope', '$state', '$location', '$window', '$websocket', '$interval', 'Authentication', 'User'];

/**
 * @name run
 * @desc Update xsrf $http headers to align with Django's defaults
 */
function run($http, $rootScope, $state, $location, $window, $websocket, $interval, Authentication, User) {
    $http.defaults.xsrfHeaderName = 'X-CSRFToken';
    $http.defaults.xsrfCookieName = 'csrftoken';

    $rootScope.$on("$stateChangeStart",
        function (event, toState, toParams, fromState, fromParams) {
            var isAuthenticated = Authentication.isAuthenticated();

            if (toState.authenticate && !isAuthenticated) {
                $rootScope.isLoggedIn = isAuthenticated;
                $rootScope.account = null;

                $state.go('login');

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

    $rootScope.initializeWebSocket = function () {
        $rootScope.ws = $websocket.$new({
            url: $rootScope.getWebsocketUrl() + '/ws/inbox?subscribe-user',
            lazy: true,
            reconnect: true
        });

        //var timeout = null;

        $rootScope.ws
            .$on('$message', function (data) {
                $rootScope.$broadcast('message', data);
            })
            .$on('$close', function () {
                //$interval.cancel(timeout);
            })
            .$on('$open', function () {
                //timeout = $interval(function(){
                //    User.setOnline();
                //}, 30000);
            })
            .$open();
    };

    $rootScope.closeWebSocket = function () {
        if($rootScope.ws) {
            $rootScope.ws.$close();
        }
    };

    $rootScope.openChat = function (requester) {
        $rootScope.$broadcast('conversation', requester);
    };

    var isAuthenticated = Authentication.isAuthenticated();

    if (isAuthenticated) {
        $rootScope.initializeWebSocket();
    }

    $window.onbeforeunload = function (evt) {
        $rootScope.closeWebSocket();
    }

}
