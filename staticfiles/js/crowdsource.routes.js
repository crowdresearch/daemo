(function () {
    'use strict';

    angular
        .module('crowdsource.routes', ['ngRoute', 'ui.router'])
        .config(config);

    config.$inject = ['$urlRouterProvider', '$stateProvider'];

    /**
     * @name config
     * @desc Define valid application routes
     */
    function config($urlRouterProvider, $stateProvider) {
        $urlRouterProvider
            .otherwise('/');

        //Views
        var navbar = {
            controller: 'NavbarController',
            controllerAs: 'vm',
            templateUrl: '/static/templates/layout/navbar.html'
        };

        var footer = {
            controller: 'NavbarController',
            controllerAs: 'vm',
            templateUrl: '/static/templates/layout/footer.html'
        };

        var home = {
            templateUrl: '/static/templates/home.html',
            controller: 'HomeController'
        };

        var worker = {
            templateUrl: '/static/templates/worker/worker.html',
            controller: 'HomeController'
        };

        var register = {
            controller: 'RegisterController',
            controllerAs: 'vm',
            templateUrl: '/static/templates/authentication/register.html'
        };

        var terms = {
            templateUrl: '/static/templates/terms.html',
            controller: 'RegisterController'
        };

        var login = {
            controller: 'LoginController',
            controllerAs: 'vm',
            templateUrl: '/static/templates/authentication/login.html'
        };

        var profile = {
            templateUrl: '/static/templates/profile.html',
            controller: 'HomeController'
        };

        var requester = {
            templateUrl: '/static/templates/requester/home.html',
            controller: 'HomeController'
        };

        var ranking = {
            templateUrl: '/static/templates/ranking/requesterrank.html',
            controller: 'RankingController'
        };

        var tasklistSearch = {
            templateUrl: '/static/templates/tasksearches/tasklistSearch.html',
            controller: 'taskSearchGridController'
        };

        var tasklist = {
            templateUrl: '/static/templates/task/tasklist.html',
            controller: 'taskController'
        };

        var imageLabel = {
            templateUrl: '/static/templates/task/ImageLabel.html',
            controller: 'taskController'
        };

        var contact = {
            templateUrl: '/static/templates/contact.html',
            controllerAs: 'vm',
            controller: 'HomeController'
        };

        var contributors = {
            templateUrl: function ($stateParams) {
                return '/static/templates/contributors/home.html';
            }
        };

        var contributorDetail = {
            templateUrl: function ($stateParams) {
                return '/static/templates/contributors/' + $stateParams.name + '.html';
            }
        };


        //States
        $stateProvider
            .state('home', {
                url: '/',
                views: {
                    'content': home,
                    'navbar': navbar,
                    'footer': footer
                },
                authenticate: false
            })
            .state('register', {
                url: '/register',
                views: {
                    'content': register,
                    'navbar': navbar,
                    'footer': footer
                },
                authenticate: false
            })
            .state('terms', {
                url: '/terms',
                views: {
                    'content': terms,
                    'navbar': navbar,
                    'footer': footer
                },
                authenticate: false
            })
            .state('login', {
                url: '/login',
                views: {
                    'content': login,
                    'navbar': navbar,
                    'footer': footer
                },
                authenticate: false
            })
            .state('profile', {
                url: '/profile',
                views: {
                    'content': profile,
                    'navbar': navbar,
                    'footer': footer
                },
                authenticate: false
            })
            .state('worker', {
                url: '/worker',
                views: {
                    'content': worker,
                    'navbar': navbar,
                    'footer': footer
                },
                authenticate: false
            })
            .state('requester', {
                url: '/requester',
                views: {
                    'content': requester,
                    'navbar': navbar,
                    'footer': footer
                },
                authenticate: false
            })


            .state('ranking', {
                url: '/ranking',
                views: {
                    'content': ranking,
                    'navbar': navbar,
                    'footer': footer
                },
                authenticate: false
            })

            .state('tasklist', {
                url: '/tasks',
                views: {
                    'content': tasklist,
                    'navbar': navbar,
                    'footer': footer
                },
                authenticate: false
            })
            .state('tasklistSearch', {
                url: '/tasks/search',
                views: {
                    'content': tasklistSearch,
                    'navbar': navbar,
                    'footer': footer
                },
                authenticate: false
            })
            .state('imageLabel', {
                url: '/imageLabel',
                views: {
                    'content': imageLabel,
                    'navbar': navbar,
                    'footer': footer
                },
                authenticate: false
            })
            .state('contributors', {
                url: '/contributors',
                views: {
                    'content': contributors,
                    'navbar': navbar,
                    'footer': footer
                },
                authenticate: false
            })
            .state('contributorDetail', {
                url: '/contributors/:name',
                views: {
                    'content': contributorDetail,
                    'navbar': navbar,
                    'footer': footer
                },
                authenticate: false
            })
            .state('contact', {
                url: '/contact',
                views: {
                    'content': contact,
                    'navbar': navbar,
                    'footer': footer
                },
                authenticate: false
            })
        ;
    }
})();
