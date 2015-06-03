/**
* HomeController
* @namespace crowdsource.home.controllers
*/
(function () {
  'use strict';

  angular
    .module('crowdsource.home.controllers')
    .controller('HomeController', HomeController);

  HomeController.$inject = ['$location', '$scope', 'Authentication'];

  /**
  * @namespace HomeController
  */
  function HomeController($location, $scope, Authentication) {
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
          progress : 70 
        },
        {
          name : 'Sentiment Analysis',
          progress : 60 
        },
        {
          name : 'Academic Survey',
          progress : 40 
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
  }
})();