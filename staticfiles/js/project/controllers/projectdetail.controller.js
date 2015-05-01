/**
 * Created by milad on 5/1/15.
 */

/**
 * Created by milad on 4/30/15.
 */


(function () {
  'use strict';

  angular
    .module('crowdsource.project.controllers')
    .controller('ProjectDetailController', ProjectDetailController);

  ProjectDetailController.$inject = ['$scope','$http','$routeParams','Authentication'];

  /**
  * @namespace AddProjectController
  */
  function ProjectDetailController($scope,$http,$routeParams,Authentication) {
$http.get('/api-auth/v1/project/own?projectid='+ $routeParams.ProjectID).success(function(data, config){
   $scope.project=data[0];
});



console.log($routeParams.ProjectID);

  }


})();