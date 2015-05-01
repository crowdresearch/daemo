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
    $scope.submit = function() {
        var data = { subject: $scope.subject };
        $http.post('/api-auth/v1/project/own/', data)
            .success(function(out_data) {
            });
    }
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
  }



})();