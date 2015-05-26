angular
  .module('crowdsource', [
    // third party modules
    'angular-loading-bar',
    'ui.bootstrap',
    'ngAnimate',
    'ngSanitize',
    'mgcrea.ngStrap',
    // local modules
    'crowdsource.config',
    'crowdsource.routes',
    'crowdsource.authentication',
    'crowdsource.layout',
    'crowdsource.home',
    'crowdsource.ranking',
    'crowdsource.tasksearch',
    'crowdsource.tasks',
    'crowdsource.directives',
  ]);

angular
  .module('crowdsource')
  .run(run);

run.$inject = ['$http'];

/**
* @name run
* @desc Update xsrf $http headers to align with Django's defaults
*/
function run($http) {
  $http.defaults.xsrfHeaderName = 'X-CSRFToken';
  $http.defaults.xsrfCookieName = 'csrftoken';
}