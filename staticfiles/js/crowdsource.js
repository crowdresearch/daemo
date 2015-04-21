angular
  .module('crowdsource', [
    'crowdsource.config',
    'crowdsource.routes',
    'crowdsource.authentication',
    'crowdsource.layout',
    'crowdsource.home',
    // ...
  ]);

angular
  .module('crowdsource.config', []);

angular
  .module('crowdsource.routes', ['ngRoute']);

angular
  .module('crowdsource.authentication', ['ngCookies']);

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