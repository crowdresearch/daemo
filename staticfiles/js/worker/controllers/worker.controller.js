/**
* WorkerProfileController
* @namespace crowdsource.worker.controllers
*/
(function () {
  'use strict';

  angular
    .module('crowdsource.worker.controllers')
    .controller('WorkerProfileController', WorkerProfileController);

  WorkerProfileController.$inject = ['$location', '$scope', 'Authentication'];

  /**
  * @namespace HomeController
  */
  function WorkerProfileController($location, $scope, Authentication) {
    var vm = this;
    //Static mock JSON for worker homepage
    $scope.user = {
      rank : 45,
      totalProjects : 13,
      currentProjects : 10,
      earnings: '50,000',
      upcomingDeadline : 'July 10',
      realTimeTaskProgress : [{
          name : 'Image Labeling',
          completed : false 
        },
        {
          name : 'Sentiment Analysis',
          completed : true 
        },
        {
          name : 'Academic Survey',
          completed : true 
        }
      ],
      skills : [
        {
          name : 'Data Entry',
          total : 120
        },
        {
          name : 'Analysis',
          total : 30
        },
        {
          name : 'Writing',
          total : 50
        }
      ],
      approvedTasks : [
        {
          name : 'Data Entry'
        },
        {
          name : 'Writing'
        },
        {
          name : 'Image Labeling'
        }
      ],
      bookmarkedRequesters : [
        {
          name : 'MIT'
        },
        {
          name : 'Media Lab'
        },
        {
          name : 'Social Computing Lab'
        }
      ],
      socialLinks : {
          fb : 'http://facebook.com/testProfile',
          twitter : 'http://twitter.com/testProfile',
          gplus : 'plus.google.com/testProfile'
      }
    };
    var numberOfRealTimeTasks = $scope.user.realTimeTaskProgress.length, count=0;
    for(var i=0; i<numberOfRealTimeTasks; i++) {
      if($scope.user.realTimeTaskProgress[i].completed == true)
        {
          count++;
        }
    }
    $scope.progress = parseInt(count/numberOfRealTimeTasks *100).toFixed(2);
  }
})();