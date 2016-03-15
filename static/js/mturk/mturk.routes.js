(function () {
    'use strict';

    angular
        .module('mturk.routes', ['ui.router'])
        .config(config);

    config.$inject = ['$stateProvider', '$urlRouterProvider'];

    /**
     * @name config
     * @desc Define valid application routes
     */
    function config($stateProvider, $urlRouterProvider) {

        // Views
        var mturk = {
            controller: 'HITController',
            controllerAs: 'hit',
            templateUrl: '/static/templates/hit/base.html'
        };

        // States
        $stateProvider

            .state('mturk', {
                url: '/mturk/task/?taskId&assignmentId&hitId&workerId',
                views: {
                    'content': mturk
                },
                authenticate: false
            })
        ;

        $urlRouterProvider.otherwise("/mturk");
    }
})();
