angular
    .module('crowdsource', [
        // third party modules
        'ngFx',
        'ngMessages',
        'ngAnimate',
        'ngSanitize',
        'ngMaterial',
        'ngFileUpload',
        'ng-sortable',
        'ui.router',
        'ngWebsocket',
        'hc.marked',
        'nvd3',
        'angularMoment',
        'hljs',
        'md.time.picker',

        // local modules
        'crowdsource.config',
        'crowdsource.interceptor',
        'crowdsource.routes',
        'crowdsource.localstorage',
        'crowdsource.authentication',
        'crowdsource.layout',
        'crowdsource.rating',
        'crowdsource.task',
        'crowdsource.directives',
        'crowdsource.services',
        'crowdsource.project',
        'crowdsource.payment',
        'crowdsource.task-feed',
        'crowdsource.task-worker',
        'crowdsource.template',
        'crowdsource.user',
        'crowdsource.helpers',
        'crowdsource.message',
        'crowdsource.docs'

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

                $state.go('auth.login', {next: $state.href(toState, toParams)});

                event.preventDefault();
            }
            $rootScope.pageTitle = toState.title || 'Daemo';
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
        $rootScope.closeWebSocket();

        $rootScope.ws = $websocket.$new({
            url: $rootScope.getWebsocketUrl() + '/ws/notifications?subscribe-user',
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
        if ($rootScope.ws) {
            $rootScope.ws.$close();
        }
    };

    $rootScope.openChat = function (requester) {
        $rootScope.$broadcast('conversation', requester);
    };

    var isAuthenticated = Authentication.isAuthenticated();

    if (isAuthenticated) {
        $rootScope.initializeWebSocket(); //TODO uncomment when messages added back
    }

    $window.onbeforeunload = function (evt) {
        $rootScope.closeWebSocket();
    }

}
