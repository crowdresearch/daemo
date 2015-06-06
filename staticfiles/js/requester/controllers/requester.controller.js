/**
* RequesterProfileController
* @namespace crowdsource.requester.controllers
*/
(function () {
  'use strict';

  angular
    .module('crowdsource.requester.controllers')
    .controller('RequesterProfileController', RequesterProfileController);

  RequesterProfileController.$inject = ['$location', '$scope', 'Authentication'];

  /**
  * @namespace RequesterProfileController
  */
  function RequesterProfileController($location, $scope, Authentication) {
    var vm = this;
    $scope.requesterProfile = {
     rank : 45,
     upcomingDeadline : 'July 10',
     summary : [
       {
         name : 'Total Projects',
         amount : 400
       },
       {
         name : 'Current Projects',
         amount : 20
       },
       {
         name : 'Waiting for Approval',
         amount : 10
       },
     ],
     realTimeTaskProgress : [{
         name : 'Image Labeling',
         completed : false,
         percent : 72
       },
       {
         name : 'Sentiment Analysis',
         completed : false,
         percent : 33
       },
       {
         name : 'Academic Survey',
         completed : true,
         percent : 100
       }
     ],
     paymentActivities : [
       {
         name : 'Survey',
         amount : 120
       },
       {
         name : 'Writing',
         amount : 50
       },
       {
         name : 'Total',
         amount : 170
       },
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
     bookmarkedWorkers : [
       {
         name : 'John Lennon'
       },
       {
         name : 'George Harrison'
       },
       {
         name : 'Paul McCartney'
       }
     ],
     remainingBalance : [
       {
         name : 'Survey',
         amount : 12
       },
       {
         name : 'Writing',
         amount : 5
       },
       {
         name : 'Total',
         amount : 17
       },
     ],
     socialLinks : {
         fb : 'http://facebook.com/testProfile',
         twitter : 'http://twitter.com/testProfile',
         gplus : 'plus.google.com/testProfile'
     }
   };


  }
})();