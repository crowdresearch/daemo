/**
 * Created by dmorina on 16/04/15.
 */
(function () {
      'use strict';

      angular
        .module('crowdresearch.routes',['ngRoute'])
        .config(config);

      config.$inject = ['$routeProvider'];

      function config($routeProvider) {
        $routeProvider.when('/register', {
          controller: 'RegisterController',
          templateUrl: '/static/templates/registration/register.html'
        }).when('/login', {
          controller: 'LoginController',
          templateUrl: '/static/templates/login.html'
        }).when('/forgot-password',{
            controller:'ForgotPasswordController',
            templateUrl: '/templates/registration/forgot_password.html'
        }).when('/users/:username',{
            controller:'ProfileController',
            templateUrl: '/templates/profile.html'
        })
        .when('/logout',{
            controller:'LogoutController'
            //templateUrl: '/templates/login.html'
        })
        .otherwise('/',{templateUrl:'/templates/home.html'});
        //$locationProvider.html5Mode(true);
      }
})();