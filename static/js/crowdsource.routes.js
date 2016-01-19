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
                templateUrl: '/static/templates/task-feed/main.html',
                controller: 'TaskFeedController',
                controllerAs: 'taskfeed',
                authenticated: true
            })
            .when('/dashboard', {
                templateUrl: '/static/templates/dashboard/dashboard.html',
                controller: 'DashboardController',
                controllerAs: 'dashboard',
                authenticated: true
            })
            .when('/messages', {
                templateUrl: '/static/templates/message/base.html',
                authenticated: true
            })
            .when('/profile', {
                templateUrl: '/static/templates/user/profile.html',
                controller: 'UserController',
                controllerAs: 'vm',
                authenticated: true
            })
            .when('/userskills', {
                templateUrl: '/static/templates/worker/account-skills.html',
                authenticated: true
            })
            .when('/requester', {
                templateUrl: '/static/templates/requester/home.html',
                controller: 'RequesterProfileController',
                authenticated: true
            })
            .when('/task/:taskId/:returned?', {
                templateUrl: '/static/templates/task/base.html',
                controller: 'TaskController',
                controllerAs: 'task',
                authenticated: true
            })
            .when('/register', {
                controller: 'RegisterController',
                controllerAs: 'register',
                templateUrl: '/static/templates/authentication/register.html'
            })

            .when('/login', {
                controller: 'LoginController',
                controllerAs: 'login',
                templateUrl: '/static/templates/authentication/login.html'
            })
            .when('/change-password', {
                controller: 'AuthSettingsController',
                controllerAs: 'auth',
                templateUrl: '/static/templates/authentication/change-password.html',
                authenticated: true
            })
            .when('/account-activation/:activation_key', {
                controller: 'AuthSettingsController',
                controllerAs: 'auth',
                templateUrl: '/static/templates/authentication/activate-account.html'
            })
            .when('/forgot-password', {
                controller: 'AuthSettingsController',
                controllerAs: 'auth',
                templateUrl: '/static/templates/authentication/forgot-password.html'
            })
            .when('/reset-password/:reset_key/:enable', {
                controller: 'AuthSettingsController',
                controllerAs: 'auth',
                templateUrl: '/static/templates/authentication/reset-password.html'
            })

            .when('/payment-success', {
                controller: 'PaymentController',
                controllerAs: 'vm',
                templateUrl: '/static/templates/payment/success.html',
                authenticated: true
            })

            .when('/payment-cancelled', {
                controller: 'PaymentController',
                controllerAs: 'vm',
                templateUrl: '/static/templates/payment/cancelled.html',
                authenticated: true
            })

            .when('/create-project/:projectId', {
                controller: 'ProjectController',
                controllerAs: 'project',
                templateUrl: '/static/templates/project/authoring.html',
                authenticated: true
            })

            .when('/task-feed/:projectId?', {
                controller: 'TaskFeedController',
                controllerAs: 'taskfeed',
                templateUrl: '/static/templates/task-feed/main.html',
                authenticated: true
            })
            .when('/my-projects', {
                controller: 'MyProjectController',
                controllerAs: 'project',
                templateUrl: '/static/templates/project/my-projects.html',
                authenticated: true
            })
            .when('/my-tasks', {
                templateUrl: '/static/templates/project/my-tasks.html',
                controller: 'MyTasksController',
                controllerAs: 'myTasks',
                authenticated: true
            })
            .when('/project-review/_p/:projectId', {
                controller: 'ProjectReviewController',
                controllerAs: 'review',
                templateUrl: '/static/templates/project/submission-review.html',
                authenticated: true,
                resolve: {
                    resolvedData: function ($route, Project) {
                        return Project.retrieve($route.current.params.projectId);
                    }
                }
            })
            .when('/api/google-auth-finish?:code', {
                controller: 'DriveController',
                templateUrl: '/static/templates/user/drive.html',
                authenticated: true
            })

            .when('/contributors', {
                controller: 'ContributorController',
                controllerAs: 'vm',
                templateUrl: '/static/templates/contributor/home.html'
            })

            //.when('/contributors/:contributor', {
            //    templateUrl: function(params){
            //        return '/static/templates/contributor/' + params.contributor + '.html';
            //    }
            //})

            .otherwise('/');
    }
})();
