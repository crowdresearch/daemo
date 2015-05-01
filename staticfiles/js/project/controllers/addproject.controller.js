/**
 * Created by milad on 4/30/15.
 */


(function () {
  'use strict';

  angular
    .module('crowdsource.project.controllers',['ui.bootstrap'])
    .controller('AddProjectController', AddProject);

  AddProject.$inject = ['$scope','$http'];

  /**
  * @namespace AddProjectController
  */
  function AddProject($scope,$http) {
$scope.today = function() {
    $scope.dt = new Date();

  };
  $scope.today();

  $scope.clear = function () {
    $scope.dt = null;
  };

  // Disable weekend selection
  $scope.disabled = function(date, mode) {
    return ( mode === 'day' && ( date.getDay() === 0 || date.getDay() === 6 ) );
  };

  $scope.toggleMin = function() {
    $scope.minDate = $scope.minDate ? null : new Date();
  };
  $scope.toggleMin();

  $scope.open = function($event) {
    $event.preventDefault();
    $event.stopPropagation();

    $scope.opened = true;
  };

  $scope.dateOptions = {
    formatYear: 'yy',
    startingDay: 1
  };

  $scope.formats = ['dd-MMMM-yyyy', 'yyyy/MM/dd', 'dd.MM.yyyy', 'shortDate'];
  $scope.format = $scope.formats[0];


      var vm=this;

      $scope.postit=postit;
            $scope.vm=vm;


      function postit()
      {
          $http({
        url: "/api-auth/v1/project/own/",
        method: "POST",
        data: {

          project_name: vm.project_name,

            project_date: $scope.dt

        }
      }).success(function(){
              console.log('okkeey');
          });
      }
  }



})();