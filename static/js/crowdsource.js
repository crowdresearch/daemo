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

  $rootScope.$on('$routeChangeStart', function (event, next) {
      var isAuthenticated = Authentication.isAuthenticated();

      if (!isAuthenticated && next.hasOwnProperty('$$route') && next.$$route.hasOwnProperty('authenticated') && next.$$route.authenticated) {
          event.preventDefault();

          $rootScope.isLoggedIn = isAuthenticated;
          $rootScope.account = null;

          $location.path('/login');
      }
    });

   $rootScope.theme = 'default';

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
