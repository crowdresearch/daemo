angular
    .module('crowdsource-lite', [
        // third party modules
        'ngMessages',
        'ngAnimate',
        'ngSanitize',
        'ngMaterial',
        // local modules
        //'crowdsource.config',
        'crowdsource.interceptor',
        'crowdsource.routes',
        'crowdsource.authentication',
        'crowdsource.services'
    ]);

angular
    .module('crowdsource')
    .run(run);

run.$inject = ['$http', '$rootScope'];

/**
 * @name run
 * @desc Update xsrf $http headers to align with Django's defaults
 */
function run($http, $rootScope) {
    $http.defaults.xsrfHeaderName = 'X-CSRFToken';
    $http.defaults.xsrfCookieName = 'csrftoken';

    $rootScope.theme = 'default';
}
