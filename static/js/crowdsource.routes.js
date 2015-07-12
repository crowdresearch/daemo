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
      //templateUrl: '/static/templates/intro.html'
      templateUrl: '/static/templates/task-feed/main.html',
      controller: 'TaskFeedController',
      controllerAs: 'taskfeed'
    })
   
    .when('/home', {
      templateUrl: '/static/templates/home.html',
      controller: 'HomeController'
    })
    .when('/messages', {
      templateUrl: '/static/templates/messages/base.html'
    })
    .when('/profile', {
      templateUrl: '/static/templates/worker/account-basic-info.html'
    })
    
    .when('/userskills', {
      templateUrl: '/static/templates/worker/account-skills.html'
    })

    .when('/worker', {
      templateUrl: '/static/templates/home.html',
      controller: 'WorkerProfileController',
      controllerAs: 'vm'
    })

    .when('/ranking', {
      templateUrl: '/static/templates/ranking/requesterrank.html',
      controller: 'RankingController'
    })


    //We will merge tasklistSearch and tasklist to one component, please keep it separate for now.
    .when('/tasklistSearch', {
    templateUrl: '/static/templates/tasksearches/tasklistSearch.html',
    controller: 'taskSearchGridController'
    })

    .when('/requester', {
      templateUrl: '/static/templates/requester/home.html',
      controller: 'RequesterProfileController'
    })

    .when('/tasklist', {
      templateUrl: '/static/templates/task/tasklist.html',
      controller: 'taskController'
    })

    .when('/task/:taskId', {
      templateUrl: '/static/templates/task/detail.html',
      controller: 'taskDetailController',
      controllerAs: 'taskDetail'
    })

    .when('/task-worker/:taskWorkerId', {
      templateUrl: '/static/templates/task-worker/detail.html',
      controller: 'taskWorkerDetailController',
      controllerAs: 'taskWorkerDetail'
    })

    .when('/monitor/:projectId', {
      templateUrl: '/static/templates/task/monitor.html',
      controller: 'MonitorController'
    })

    .when('/ImageLabel', {
      templateUrl: '/static/templates/task/ImageLabel.html'
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

    .when('/terms', {
      templateUrl: '/static/templates/terms.html'
    })

    .when('/contributors', {
      templateUrl: '/static/templates/contributors/home.html'
    })
    
     .when('/projectStart', {
        controller: 'ProjectController',
        controllerAs: 'project',
        templateUrl :'/static/templates/project/start.html'
    })
    .when('/payment', {
        controller: 'ProjectController',
        controllerAs: 'project',
        templateUrl :'/static/templates/project/payment.html'
    })
    
    .when('/milestones', {
        controller: 'ProjectController',
        controllerAs: 'project',
        templateUrl :'/static/templates/project/milestones.html'
    })

    .when('/milestones/createtemplate', {
        controller: 'CreateTemplateController',
        controllerAs: 'vm',
        templateUrl :'/static/templates/project/milestones/createtemplate.html'
    })

    .when('/milestones/:id/viewtemplate', {
        templateUrl: '/static/templates/project/milestones/viewtemplate.html',
        controller: 'ViewTemplateCtrl'
    })
    
    .when('/review', {
        controller: 'ProjectController',
        controllerAs: 'project',
        templateUrl :'/static/templates/project/summary.html'
    })
    
    .when('/create-project/:projectStepId', {
        controller: 'ProjectController',
        controllerAs: 'project',
        templateUrl :'/static/templates/project/base.html'
    })

    .when('/task-feed', {
      controller: 'TaskFeedController',
      controllerAs: 'taskfeed',
      templateUrl :'/static/templates/task-feed/main.html'
    })
    .when('/create-template', {
        controller: 'TemplateController',
        controllerAs: 'template',
        templateUrl :'/static/templates/template/container.html'
    })
    .when('/my-projects', {
            controller: 'ProjectController',
            controllerAs: 'project',
            templateUrl :'/static/templates/project/my-projects.html'
    })
    .when('/api/google-auth-finish?:code', {
        controller: 'DriveController',
        templateUrl :'/static/templates/user/drive.html'
    })
    .when('/bookmarked-projects', {
      templateUrl: '/static/templates/task-feed/bookmarked.html'
    })
    .when('/contributors/:contributorName', {
      templateUrl: function(params){
          return '/static/templates/contributors/'+params.contributorName+'.html';
      }
    })
    .otherwise('/');
  }
})();
