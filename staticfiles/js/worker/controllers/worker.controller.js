/**
* WorkerProfileController
* @namespace crowdsource.worker.controllers
*/
(function () {
  'use strict';

  angular
    .module('crowdsource.worker.controllers')
    .controller('WorkerProfileController', WorkerProfileController);

  WorkerProfileController.$inject = ['$location', '$scope', 'Authentication', 'Worker'];

  /**
  * @namespace WorkerProfileController
  */
  function WorkerProfileController($location, $scope, Authentication, Worker) {
    var vm = this;
    Worker.getWorkerPrivateProfile().success(function(data) {
      $scope.user = data;
      var numberOfRealTimeTasks = $scope.user.realTimeTaskProgress.length, count=0;
      for(var i=0; i<numberOfRealTimeTasks; i++) {
      if($scope.user.realTimeTaskProgress[i].completed == true)
        {
          count++;
        }
      }
      $scope.progress = parseInt(count/numberOfRealTimeTasks *100).toFixed(2);
    });

    Worker.getWorkerTaskPortfolio().success(function(data) {
      $scope.WorkerTaskPortfolio = data;
    });
    
    
  }


})();