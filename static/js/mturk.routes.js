(function () {
    'use strict';

    angular
        .module('mturk.routes', ['ngRoute'])
        .config(config);

    config.$inject = ['$routeProvider'];

    /**
     * @name config
     * @desc Define valid application routes
     */
    function config($routeProvider) {
        $routeProvider
            .when('/mturk', {
                templateUrl: '/static/templates/task-feed/register.html',
                controller: 'TaskController',
                //controllerAs: 'taskfeed',
                //authenticated: true
            })

            .when('/mturk-external/:task_id/:assignmentId/:workerId/:hitId/', {
                controller: 'TaskController',
                //controllerAs: 'login',
                templateUrl: '/static/templates/authentication/register.html'
            })
            .otherwise('/mturk');
    }
})();
