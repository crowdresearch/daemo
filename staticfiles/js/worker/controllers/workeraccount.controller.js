/**
* WorkerAccountController
* @namespace crowdsource.worker.controllers
*/
(function () {
  'use strict';

  angular
    .module('crowdsource.worker.controllers')
    .controller('WorkerAccountController', WorkerAccountController);

  WorkerAccountController.$inject = ['$location', '$scope', '$routeParams', 'Authentication', 'Worker'];

  /**
  * @namespace WorkerAccountController
  */
  function WorkerAccountController($location, $scope, $routeParams, Authentication, Worker) {
    var vm = this;
    // First check if route is null, then redirect to basic-info
    if (!Object.keys($routeParams).length) {
      $location.path('/profile/basic-info');
      return;
    }
    

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