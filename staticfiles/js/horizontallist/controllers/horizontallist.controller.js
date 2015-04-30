/**
* HorizontalListController
* @namespace crowdsource.horizontallist.controllers
*/
(function () {
  'use strict';

  angular
    .module('crowdsource.horizontallist.controllers')
    .controller('HorizontalListController',  HR);

  HR.$inject = [ '$scope','$http'];

  /**
  * @namespace HorizontalListController
  */
  function HR( $scope,$http) {


      $http.get('api-auth/v1/project/own/').success(function(data,config)
      {
          $scope.myprojects=data;
      });
  }
})();