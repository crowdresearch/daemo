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

        .when('/contributors/ansuman', {
      templateUrl: '/static/templates/contributors/ansuman.html'
    })

    .when('/contributors/anirudh', {
      templateUrl: '/static/templates/contributors/anirudh.html'
    })

  	.when('/contributors/shirish', {
      templateUrl: '/static/templates/contributors/shirish.html'
    })
    
    .when('/contributors/ard', {
      templateUrl: '/static/templates/contributors/ard.html'
    })

    .when('/contributors/narwal', {
      templateUrl: '/static/templates/contributors/narwal.html'
    })

    .when('/contributors/radhika', {
      templateUrl: '/static/templates/contributors/radhika.html'
    })

    .when('/contributors/sangm', {
      templateUrl: '/static/templates/contributors/sangm.html'
    })

    .when('/contributors/sean', {
      templateUrl: '/static/templates/contributors/sean.html'
    })
    
     .when('/contributors/leek', {
      templateUrl: '/static/templates/contributors/leek.html'
    })
 
    .when('/contributors/karan', {
      templateUrl: '/static/templates/contributors/karan.html'
    })
    
    .when('/contributors/vaidehi', {
      templateUrl: '/static/templates/contributors/vaidehi.html'
    })
    
    .when('/contributors/jason', {
      templateUrl: '/static/templates/contributors/jason.html'
    })

    .when('/contributors/lucamatsumoto', {
      templateUrl: '/static/templates/contributors/lucamatsumoto.html'
    })

    .when('/contributors/arcolife', {
      templateUrl: '/static/templates/contributors/arcolife.html'
    })
     
    .when('/contributors/AditiNath', {
      templateUrl: '/static/templates/contributors/aditinath.html'
    })

    .when('/contributors/ucerron', {
      templateUrl: '/static/templates/contributors/ucerron.html'
    })

    .when('/contributors/AmitRakesh', {
		templateUrl: '/static/templates/contributors/amitrakesh.html'
    })
	
    .when('/contributors/Milstein', {
      templateUrl: '/static/templates/contributors/milstein.html'
    })      
	 
    .when('/contributors/bmoix', {
      templateUrl: '/static/templates/contributors/bmoix.html'
    }) 
	
	.when('/contributors/vineet', {
      templateUrl: '/static/templates/contributors/vineet.html'
    })

    .when('/contributors/abhinav', {
      templateUrl: '/static/templates/contributors/abhinav.html'
    })

	.when('/contributors/Pabitra', {
      templateUrl: '/static/templates/contributors/Pabitra.html'
    })
    
  	.when('/contributors/KajalGupta', {
      templateUrl: '/static/templates/contributors/kajal.html'
    })
    
    .when('/contributors/pemmasani', {
      templateUrl: '/static/templates/contributors/pemmasani.html'
    })
    
    .when('/contributors/xiaoran', {
      templateUrl: '/static/templates/contributors/xiaoran.html'
    })

    .otherwise('/');   
  }
})();
