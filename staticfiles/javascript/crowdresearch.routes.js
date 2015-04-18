/**
 * Created by dmorina on 16/04/15.
 */
(function () {
      'use strict';

      angular
        .module('crowdresearch.routes')
        .config(config);

      config.$inject = ['$routeProvider'];

      function config($routeProvider) {
        $routeProvider.when('/register', {
          controller: 'RegisterController',
          templateUrl: '/templates/registration/register.html'
        }).when('/login', {
          controller: 'LoginController',
          templateUrl: '/templates/login.html'
        }).when('/forgot-password',{
            controller:'ForgotPasswordController',
            templateUrl: '/templates/registration/forgot_password.html'
        })
        .otherwise('/',{templateUrl:'/templates/home.html'});
      }
})();