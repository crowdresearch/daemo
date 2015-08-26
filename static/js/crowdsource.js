angular
  .module('crowdsource', [
    // third party modules
    'angular-loading-bar',
    'ui.bootstrap',
    'ngAnimate',
    'ngSanitize',
    'mgcrea.ngStrap',
    'ngMaterial',
    //'angular-oauth2',
    'ngDragDrop',
    'ui.sortable',
    'ngFileUpload',
    // local modules
    'crowdsource.config',
    'crowdsource.routes',
    'crowdsource.authentication',
    'crowdsource.dashboard',
    'crowdsource.layout',
    'crowdsource.home',
    'crowdsource.requester',
    'crowdsource.ranking',
    'crowdsource.tasksearch',
    'crowdsource.task',
    'crowdsource.monitor',
    'crowdsource.directives',
    'crowdsource.services',
    'crowdsource.worker',
    'crowdsource.skill',
    'crowdsource.project',
    'crowdsource.task-feed',
    'crowdsource.task-worker',
    'crowdsource.template',
    'crowdsource.drive',
    'crowdsource.data-table',
    'crowdsource.user',
    'crowdsource.helpers'
  ]);

angular
  .module('crowdsource')
  .run(run);

run.$inject = ['$http', '$rootScope', '$window'];

/**
* @name run
* @desc Update xsrf $http headers to align with Django's defaults
*/
function run($http, $rootScope, $window) {
  $http.defaults.xsrfHeaderName = 'X-CSRFToken';
  $http.defaults.xsrfCookieName = 'csrftoken';
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