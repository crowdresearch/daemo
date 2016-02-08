angular
    .module('mturk', [
        'ngMessages',
        'ngAnimate',
        'ngSanitize',
        'ngCookies',
        'ngMaterial',
        'mturk.config',
        'mturk.routes',
        'mturk.hit',
        'crowdsource.services',
        //'crowdsource.authentication',
        //'crowdsource.project',
        //'crowdsource.task-worker',
        'crowdsource.template'
    ]);

angular
    .module('mturk')
    .run(run);

run.$inject = ['$http', '$rootScope', '$window', '$location'];

/**
 * @name run
 * @desc Update xsrf $http headers to align with Django's defaults
 */
function run($http, $rootScope, $window, $location) {
    $http.defaults.xsrfHeaderName = 'X-CSRFToken';
    $http.defaults.xsrfCookieName = 'csrftoken';
    $rootScope.theme = 'default';

}
