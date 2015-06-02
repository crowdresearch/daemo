angular
    .module('crowdsource', [

        // third party modules
        'angular-loading-bar',
        'ui.router',
        'ui.bootstrap',
        'ngAnimate',
        'ngSanitize',
        'mgcrea.ngStrap',

        // local modules
        'crowdsource.config',
        'crowdsource.routes',
        'crowdsource.directives',
        'crowdsource.filters',

        'crowdsource.authentication',
        'crowdsource.layout',
        'crowdsource.home',
        'crowdsource.ranking',
        'crowdsource.tasksearch',
        'crowdsource.projects',
        'crowdsource.tasks',
    ]);

angular
    .module('crowdsource')
    .constant('CONSTANTS', {
        API_URL: '/api/v1'
    })
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