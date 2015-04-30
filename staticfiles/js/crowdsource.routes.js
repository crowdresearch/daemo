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
    $routeProvider.when('/', {
      templateUrl: '/static/templates/intro.html',
    }).otherwise('/')

    .when('/profile', {
      templateUrl: '/static/templates/profle.html',
      controller: 'ProfileController',
    }).otherwise('/')

    .when('/home',{
        templateUrl: '/static/templates/catalog/main.html',
      controller: 'testController',
    }).otherwise('/')

    .when('/ranking', {
      templateUrl: '/static/templates/ranking/requesterrank.html',
      controller: 'RankingController',
    }).otherwise('/')
    
    .when('/register', {
      controller: 'RegisterController',
      controllerAs: 'vm',
      templateUrl: '/static/templates/authentication/register.html'
    })
    
    .when('/login', {
      controller: 'LoginController',
      controllerAs: 'vm',
      templateUrl: '/static/templates/authentication/login.html'
    }).otherwise('/')

    .when('/terms', {
      templateUrl: '/static/templates/terms.html'
    }).otherwise('/');
  }
})();