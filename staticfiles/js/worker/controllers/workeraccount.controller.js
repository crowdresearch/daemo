/**
* WorkerAccountController
* @namespace crowdsource.worker.controllers
*/
(function () {
  'use strict';

  angular
    .module('crowdsource.worker.controllers')
    .controller('WorkerAccountController', WorkerAccountController);

  WorkerAccountController.$inject = ['$location', '$scope', '$routeParams', '$mdToast', 'Authentication', 'Worker', 'Skill'];

  /**
  * @namespace WorkerAccountController
  */
  function WorkerAccountController($location, $scope, $routeParams, $mdToast, Authentication, Worker, Skill) {
    var vm = this;
    var userAccount = Authentication.getAuthenticatedAccount();
    if (!userAccount) {
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
      Worker.removeSkill(skill.id)
      .then(function success (data) {
        getWorkerPrivatePortfolio();
      }, function (err) {
        $mdToast.showSimple('Error removing skill');
      }); 
    };

    $scope.addSkill = function addSkill() {
      if (!$scope.skillsform.$valid) {
        var errorStr = getErrorStr($scope.skillsform);
        $mdToast.showSimple(errorStr);
        return;
      }

      var skillExists = false;
      $scope.user.skills.forEach(function (skillObj) {
        if (skillObj.id === $scope.selectedSkill.id) {
          $mdToast.showSimple('You\'ve already added this skill!');
          skillExists = true;
        }
      });
      if (skillExists) { return; }

      Worker.addSkill($scope.selectedSkill.id)
      .then(function success (data) {
        $scope.selectedSkill = '';
        getWorkerPrivatePortfolio();
      }, function (err) {
        $mdToast.showSimple('Error adding skill');
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