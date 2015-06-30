/**
* WorkerAccountController
* @namespace crowdsource.worker.controllers
*/
(function () {
  'use strict';

  angular
    .module('crowdsource.worker.controllers')
    .controller('WorkerAccountController', WorkerAccountController);

  WorkerAccountController.$inject = ['$location', '$scope', '$routeParams', '$alert', 'Authentication', 'Worker', 'Skill'];

  /**
  * @namespace WorkerAccountController
  */
  function WorkerAccountController($location, $scope, $routeParams, $alert, Authentication, Worker, Skill) {
    var vm = this;
    var userAccount = Authentication.getAuthenticatedAccount();
    if (!userAccount.profile) {
      $location.path('/login');
      return;
    }

    Skill.getAllSkills().then(function (skillsData) {
      $scope.skills = skillsData[0];

      Worker.getWorkerPrivateProfile(userAccount.profile.id)
      .then(function(data) {
      
        $scope.user = data;
        var numberOfRealTimeTasks = $scope.user.realTimeTaskProgress.length, count=0;
        for(var i=0; i<numberOfRealTimeTasks; i++) {
        if($scope.user.realTimeTaskProgress[i].completed == true) {
            count++;
          }
        }
        $scope.progress = parseInt(count/numberOfRealTimeTasks *100).toFixed(2);
      
      });

    });



    Worker.getWorkerTaskPortfolio().success(function(data) {
      $scope.WorkerTaskPortfolio = data;
    });


    
    
    $scope.removeSkill = function removeSkill(skill) {
      Worker.removeSkill(user).then(function success (worker) {

      }, function (err) {
        $alert({
          title: 'Error!',
          content: 'Error removing skill',
          placement: 'top',
          type: 'danger',
          show: true});
      }); 
    };

    $scope.addSkill = function addSkill() {
      if (!$scope.skillsform.$valid) {
        var errorStr = getErrorStr($scope.skillsform);
        $alert({
          title: 'Error!',
          content: errorStr,
          placement: 'top',
          type: 'danger',
          show: true});
        return;
      }

      console.log($scope.selectedSkill);
      Worker.addSkill(user).then(function success (worker) {

      }, function (err) {
        $alert({
          title: 'Error!',
          content: 'Error adding skill',
          placement: 'top',
          type: 'danger',
          show: true});
      });
      
    };

    function getErrorStr(form) {
      var errorStr = [];
      if (form.$error.required.length) {
        form.$error.required.forEach(function (err) {
          errorStr.push(err.$name + ' is invalid');
        });
      }
      return errorStr.join(',');
    }
    

  }
})();