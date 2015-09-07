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
      templateUrl: '/static/templates/task-feed/main.html',
      controller: 'TaskFeedController',
      controllerAs: 'taskfeed',
      authenticated:true
    })
    .when('/dashboard', {
      templateUrl: '/static/templates/dashboard/dashboard.html',
      controller: 'DashboardController',
      controllerAs: 'dashboard',
      authenticated:true
    })
    .when('/messages', {
      templateUrl: '/static/templates/messages/base.html',
      authenticated:true
    })
    .when('/profile', {
      templateUrl : '/static/templates/user/profile.html',
      authenticated:true
    })
    .when('/userskills', {
      templateUrl: '/static/templates/worker/account-skills.html',
      authenticated:true
    })
    .when('/worker', {
      templateUrl: '/static/templates/home.html',
      controller: 'WorkerProfileController',
      controllerAs: 'vm',
      authenticated:true
    })
    .when('/ranking', {
      templateUrl: '/static/templates/ranking/requesterrank.html',
      controller: 'RankingController',
      authenticated:true
    })
    //We will merge tasklistSearch and tasklist to one component, please keep it separate for now.
    .when('/tasklistSearch', {
    templateUrl: '/static/templates/tasksearches/tasklistSearch.html',
    controller: 'taskSearchGridController',
    authenticated:true
    })
    .when('/requester', {
      templateUrl: '/static/templates/requester/home.html',
      controller: 'RequesterProfileController',
      authenticated:true
    })
    .when('/task/:taskId', {
      templateUrl: '/static/templates/task/base.html',
      controller: 'TaskController',
      controllerAs: 'task',
      authenticated:true
    })
    .when('/task/:taskId/:taskWorkerId/:returned?', {
      templateUrl: '/static/templates/task/base.html',
      controller: 'TaskController',
      controllerAs: 'task',
      authenticated:true
    })
    .when('/task-worker/:taskWorkerId', {
      templateUrl: '/static/templates/task-worker/detail.html',
      controller: 'taskWorkerDetailController',
      controllerAs: 'taskWorkerDetail',
      authenticated:true
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
      authenticated:true
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
    .when('/terms', {
      templateUrl: '/static/templates/terms.html'
    })

    .when('/contributors', {
      templateUrl: '/static/templates/contributors/home.html'
    })
    
     .when('/projectStart', {
        controller: 'ProjectController',
        controllerAs: 'project',
        templateUrl :'/static/templates/project/start.html',
        authenticated:true
    })
    .when('/payment', {
        controller: 'ProjectController',
        controllerAs: 'project',
        templateUrl :'/static/templates/project/payment.html',
        authenticated:true
    })
    
    .when('/milestones/:projectId', {
        controller: 'MilestoneOverviewController',
        controllerAs: 'milestone',
        templateUrl :'/static/templates/project/milestone/overview.html',
        authenticated:true
    })
    .when('/milestone-tasks/:moduleId', {
        controller: 'TaskOverviewController',
        controllerAs: 'task',
        templateUrl :'/static/templates/task/overview.html',
        authenticated:true
    })
    
    .when('/review', {
        controller: 'ProjectController',
        controllerAs: 'project',
        templateUrl :'/static/templates/project/summary.html',
        authenticated:true
    })
    
    .when('/create-project/:stepId', {
        controller: 'ProjectController',
        controllerAs: 'project',
        templateUrl :'/static/templates/project/base-create.html',
        authenticated:true
    })

    .when('/task-feed', {
      controller: 'TaskFeedController',
      controllerAs: 'taskfeed',
      templateUrl :'/static/templates/task-feed/main.html',
      authenticated:true
    })
    .when('/create-template', {
        controller: 'TemplateController',
        controllerAs: 'template',
        templateUrl :'/static/templates/template/container.html',
        authenticated:true
    })
    .when('/my-projects', {
        controller: 'MyProjectController',
        controllerAs: 'project',
        templateUrl :'/static/templates/project/my-projects.html',
        authenticated:true
    })
    .when('/add-milestone/:projectId/:stepId', {
      controller: 'ProjectController',
      controllerAs: 'project',
      templateUrl: '/static/templates/project/base-add.html',
      authenticated:true
    })
    .when('/api/google-auth-finish?:code', {
        controller: 'DriveController',
        templateUrl :'/static/templates/user/drive.html',
        authenticated:true
    })
    .when('/bookmarked-projects', {
      templateUrl: '/static/templates/task-feed/bookmarked.html',
      authenticated:true
    })
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

    .when('/contributors/geza', {
      templateUrl: '/static/templates/contributors/geza.html'
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

    .when('/contributors/damon', {
      templateUrl: '/static/templates/contributors/damon.html'
    })

  .when('/contributors/rcompton', {
      templateUrl: '/static/templates/contributors/rcompton.html'
    })

    .when('/contributors/hiroshi', {
      templateUrl: '/static/templates/contributors/hiroshi.html'
    })

    .when('/contributors/niraj', {
      templateUrl: '/static/templates/contributors/niraj.html'
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

    .when('/contributors/ramachandracn', {
      templateUrl: '/static/templates/contributors/ramachandracn.html'
    })

    .when('/contributors/saviaga', {
      templateUrl: '/static/templates/contributors/saviaga.html'
    })

    .when('/contributors/pitkofsky', {
      templateUrl: '/static/templates/contributors/pitkofsky.html'
    })

   .when('/contributors/paresh', {
      templateUrl: '/static/templates/contributors/paresh.html'
    })

    .when('/contributors/msb', {
      templateUrl: '/static/templates/contributors/msb.html'
    })

    .when('/contributors/ankita2992', {
      templateUrl: '/static/templates/contributors/ankita.html'
    })

    .when('/contributors/savage', {
      templateUrl: '/static/templates/contributors/savage.html'
    })

    .when('/contributors/mistercruz', {
      templateUrl: '/static/templates/contributors/mistercruz.html'
    })

    .when('/contributors/arshiya', {
      templateUrl: '/static/templates/contributors/arshiya.html'
    })

    .when('/contributors/vivekvinodh', {
      templateUrl: '/static/templates/contributors/vivekvinodh.html'
    })

     .when('/contributors/kevin', {
      templateUrl: '/static/templates/contributors/kevin.html'
     })

     .when('/contributors/vipul', {
      templateUrl: '/static/templates/contributors/vipul.html'
     })

     .when('/contributors/khushali', {
      templateUrl: '/static/templates/contributors/khushali.html'
     })

    .when('/contributors/riyakothari', {
    templateUrl: '/static/templates/contributors/riyakothari.html'
     })
  .when('/contributors/balaca', {
    templateUrl: '/static/templates/contributors/balaca.html'
     })
    .when('/contributors/jeerel', {
         templateUrl: '/static/templates/contributors/jeerel.html'
     })

     .when('/contributors/aditimithal', {
         templateUrl: '/static/templates/contributors/aditimithal.html'
     })

     .when('/contributors/niab', {
         templateUrl: '/static/templates/contributors/niab.html'
     })

    .when('/contributors/aginzberg', {
        templateUrl: '/static/templates/contributors/aginzberg.html'
    })
    .when('/contributors/xiaoran', {
        templateUrl: '/static/templates/contributors/xiaoran.html'
    })

    .otherwise('/');
  }
})();
