(function () {
    'use strict';

    angular
        .module('crowdsource.routes', ['ngRoute'])
        .config(config);

    config.$inject = ['$routeProvider'];

    /**
     * @name config
     * @desc Define valid application routes
     */
    function config($routeProvider) {
        $routeProvider
            .when('/', {
                templateUrl: '/static/js/task-feed/templates/main.html',
                controller: 'TaskFeedController',
                controllerAs: 'taskfeed',
                authenticated: true
            })
            .when('/dashboard', {
                templateUrl: '/static/js/dashboard/templates/dashboard.html',
                controller: 'DashboardController',
                controllerAs: 'dashboard',
                authenticated: true
            })
            .when('/messages', {
                templateUrl: '/static/js/message/templates/base.html',
                authenticated: true
            })
            .when('/profile', {
                templateUrl: '/static/js/user/templates/profile.html',
                controller: 'UserController',
                controllerAs: 'vm',
                authenticated: true
            })
            .when('/userskills', {
                templateUrl: '/static/js/worker/templates/account-skills.html',
                authenticated: true
            })
            .when('/requester', {
                templateUrl: '/static/js/requester/templates/home.html',
                controller: 'RequesterProfileController',
                authenticated: true
            })
            .when('/task/:taskId', {
                templateUrl: '/static/js/task/templates/base.html',
                controller: 'TaskController',
                controllerAs: 'task',
                authenticated: true
            })
            .when('/task/:taskId/:taskWorkerId/:returned?', {
                templateUrl: '/static/js/task/templates/base.html',
                controller: 'TaskController',
                controllerAs: 'task',
                authenticated: true
            })
            .when('/task-worker/:taskWorkerId', {
                templateUrl: '/static/js/task-worker/templates/detail.html',
                controller: 'taskWorkerDetailController',
                controllerAs: 'taskWorkerDetail',
                authenticated: true
            })
            .when('/register', {
                controller: 'RegisterController',
                controllerAs: 'register',
                templateUrl: '/static/js/authentication/templates/register.html'
            })

            .when('/login', {
                controller: 'LoginController',
                controllerAs: 'login',
                templateUrl: '/static/js/authentication/templates/login.html'
            })
            .when('/change-password', {
                controller: 'AuthSettingsController',
                controllerAs: 'auth',
                templateUrl: '/static/js/authentication/templates/change-password.html',
                authenticated: true
            })
            .when('/account-activation/:activation_key', {
                controller: 'AuthSettingsController',
                controllerAs: 'auth',
                templateUrl: '/static/js/authentication/templates/activate-account.html'
            })
            .when('/forgot-password', {
                controller: 'AuthSettingsController',
                controllerAs: 'auth',
                templateUrl: '/static/js/authentication/templates/forgot-password.html'
            })
            .when('/reset-password/:reset_key/:enable', {
                controller: 'AuthSettingsController',
                controllerAs: 'auth',
                templateUrl: '/static/js/authentication/templates/reset-password.html'
            })

            .when('/payment-success', {
                controller: 'PaymentController',
                controllerAs: 'vm',
                templateUrl: '/static/js/payment/templates/success.html',
                authenticated: true
            })

            .when('/payment-cancelled', {
                controller: 'PaymentController',
                controllerAs: 'vm',
                templateUrl: '/static/js/payment/templates/cancelled.html',
                authenticated: true
            })

            .when('/project-tasks/:projectId', {
                controller: 'TaskOverviewController',
                controllerAs: 'task',
                templateUrl: '/static/js/task/templates/overview.html',
                authenticated: true
            })

            .when('/create-project/:projectId', {
                controller: 'ProjectController',
                controllerAs: 'project',
                templateUrl: '/static/js/project/templates/authoring.html',
                authenticated: true
            })

            .when('/task-feed/:projectId?', {
                controller: 'TaskFeedController',
                controllerAs: 'taskfeed',
                templateUrl: '/static/js/task-feed/templates/main.html',
                authenticated: true
            })
            .when('/my-projects', {
                controller: 'MyProjectController',
                controllerAs: 'project',
                templateUrl: '/static/js/project/templates/my-projects.html',
                authenticated: true
            })

            .when('/api/google-auth-finish?:code', {
                controller: 'DriveController',
                templateUrl: '/static/js/user/templates/drive.html',
                authenticated: true
            })

            .when('/contributors', {
                controller: 'ContributorController',
                controllerAs: 'vm',
                templateUrl: '/static/js/contributor/templates/home.html'
            })

            //.when('/contributors/:contributor', {
            //    templateUrl: function(params){
            //        return '/static/js/contributor/templates/' + params.contributor + '.html';
            //    }
            //})

            .otherwise('/');
    }
})();
