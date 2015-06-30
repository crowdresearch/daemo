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
      getWorkerPrivatePortfolio();
    });



    Worker.getWorkerTaskPortfolio().success(function(data) {
      $scope.WorkerTaskPortfolio = data;
    });
    
    $scope.removeSkill = function removeSkill(skill) {
      Worker.removeSkill(user)
      .then(function success (data) {
        getWorkerPrivatePortfolio();
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

      Worker.addSkill($scope.user.workerId, $scope.selectedSkill.id)
      .then(function success (data) {
        getWorkerPrivatePortfolio();
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

    function getWorkerPrivatePortfolio() {
      Worker.getWorkerPrivateProfile(userAccount.profile.id)
      .then(function(data) {
      
        $scope.user = data[0];
        // Make worker id specific
        $scope.user.workerId = $scope.user.id;
        var refinedSkills = [];
        $scope.user.skills.forEach(function (skillId) {
          $scope.skills.forEach(function (skillEntry) {
            if (skillId === skillEntry.id) {
              refinedSkills.push(skillEntry);
            }
          });
        });
        $scope.user.skills = refinedSkills;
        // var numberOfRealTimeTasks = $scope.user.realTimeTaskProgress.length, count=0;
        // for(var i=0; i<numberOfRealTimeTasks; i++) {
        // if($scope.user.realTimeTaskProgress[i].completed == true) {
        //     count++;
        //   }
        // }
        // $scope.progress = parseInt(count/numberOfRealTimeTasks *100).toFixed(2);
      
      });
    }
    

  }
})();