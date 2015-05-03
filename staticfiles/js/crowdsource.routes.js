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

    .when('/home', {
      templateUrl: '/static/templates/home.html',
      controller: 'HomeController',
    }).otherwise('/')

    .when('/ranking', {
      templateUrl: '/static/templates/ranking/requesterrank.html',
      controller: 'RankingController',
    }).otherwise('/')
    
    //We will merge tasklistSearch and tasklist to one component, please keep it separate for now.
    .when('/tasklistSearch', {
    templateUrl: '/static/templates/tasksearches/tasklistSearch.html',
    controller: 'taskSearchGridController',
    }).otherwise('/')
    
    .when('/tasklist', {
      templateUrl: '/static/templates/task/tasklist.html',
      controller: 'taskController',
    }).otherwise('/')
    
      .when('/ImageLabel', {
        templateUrl: '/static/templates/task/ImageLabel.html'
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

    .when('/profile', {
      templateUrl: '/static/templates/home.html'
    }).otherwise('/')
    
    .when('/terms', {
      templateUrl: '/static/templates/terms.html'
    }).otherwise('/');   
  }
})();