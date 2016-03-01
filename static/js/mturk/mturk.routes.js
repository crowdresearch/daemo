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
                url: '/mturk',
                views: {
                    'content': mturk
                },
                authenticate: false
            })

            .state('mturk_external', {
                url: '/mturk-external/:task_id/:assignmentId/:workerId/:hitId/',
                views: {
                    'content': mturk
                },
                authenticate: false
            })
        ;

        $urlRouterProvider.otherwise("/mturk");
    }
})();
