/**
* RequesterProfileController
* @namespace crowdsource.home.controllers
*/
(function () {
  'use strict';

  angular
    .module('crowdsource.requester.controllers')
    .controller('RequesterProfileController', RequesterProfileController);

  RequesterProfileController.$inject = ['$location', '$scope', 'Authentication'];

  /**
  * @namespace HomeController
  */
  function RequesterProfileController($location, $scope, Authentication) {
    var vm = this;
    $scope.requesterProfile = {
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


  }
})();