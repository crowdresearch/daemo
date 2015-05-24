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
    })

    .when('/home', {
      templateUrl: '/static/templates/home.html',
      controller: 'HomeController',
    })

    .when('/ranking', {
      templateUrl: '/static/templates/ranking/requesterrank.html',
      controller: 'RankingController',
    })
    
    //We will merge tasklistSearch and tasklist to one component, please keep it separate for now.
    .when('/tasklistSearch', {
    templateUrl: '/static/templates/tasksearches/tasklistSearch.html',
    controller: 'taskSearchGridController',
    })
    
    .when('/requester', {
      templateUrl: '/static/templates/requester/home.html',
      controller: 'HomeController',
    })
    
    .when('/tasklist', {
      templateUrl: '/static/templates/task/tasklist.html',
      controller: 'taskController',
    })
    
    .when('/ImageLabel', {
      templateUrl: '/static/templates/task/ImageLabel.html'
    })
      
    .when('/register', {
      controller: 'RegisterController',
      controllerAs: 'vm',
      templateUrl: '/static/templates/authentication/register.html'
    })
    
    .when('/login', {
      controller: 'LoginController',
      controllerAs: 'vm',
      templateUrl: '/static/templates/authentication/login.html'
    })

    .when('/profile', {
      templateUrl: '/static/templates/home.html'
    })
    
    .when('/terms', {
      templateUrl: '/static/templates/terms.html'
    })

    .when('/contributors', {
      templateUrl: '/static/templates/contributors/home.html'
    })

  /**
   * Location for contributor urls. Include your personal page url here.
   */
    .when('/contributors/rohit', {
      templateUrl: '/static/templates/contributors/rohit.html'
    })

    .when('/contributors/amx', {
      templateUrl: '/static/templates/contributors/amx.html'
    })

    .when('/contributors/aneesha', {
      templateUrl: '/static/templates/contributors/aneesha.html'
    })

 	.when('/contributors/shirish', {
      templateUrl: '/static/templates/contributors/shirish.html'
    })
    
    .when('/contributors/ard', {
      templateUrl: '/static/templates/contributors/ard.html'
    })

    .when('/contributors/sean', {
      templateUrl: '/static/templates/contributors/sean.html'
    })
    
    .when('/contributors/vaidehi', {
      templateUrl: '/static/templates/contributors/vaidehi.html'
    })

    .otherwise('/');   
  }
})();
