angular
  .module('crowdsource', [
    // third party modules
    'angular-loading-bar',
    'ui.bootstrap',
    'ngAnimate',
    'ngSanitize',
    'mgcrea.ngStrap',
        'ngMaterial',
        'angular-oauth2',
    // local modules
    'crowdsource.config',
    'crowdsource.routes',
    'crowdsource.authentication',
    'crowdsource.layout',
    'crowdsource.home',
    'crowdsource.requester',
    'crowdsource.ranking',
    'crowdsource.tasksearch',
    'crowdsource.tasks',
    'crowdsource.monitor',
    'crowdsource.directives',
    'crowdsource.services',
    'crowdsource.worker',
    'crowdsource.project',
    'crowdsource.task-feed'
  ]);

angular
  .module('crowdsource')
  .run(run);

run.$inject = ['$http', '$rootScope', '$window', 'OAuth'];

/**
* @name run
* @desc Update xsrf $http headers to align with Django's defaults
*/
function run($http, $rootScope, $window, OAuth) {
  $http.defaults.xsrfHeaderName = 'X-CSRFToken';
  $http.defaults.xsrfCookieName = 'csrftoken';
  $rootScope.$on('oauth:error', function(event, rejection) {
    if ('invalid_grant' === rejection.data.error) {
      return;
    }
    if ('invalid_token' === rejection.data.error) {
      return OAuth.getRefreshToken();
    }
    return $window.location.href = '/login?error_reason=' + rejection.data.error;
  });
}