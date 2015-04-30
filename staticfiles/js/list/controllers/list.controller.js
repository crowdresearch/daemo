/**
* ListController
* @namespace crowdsource.list.controllers
*/
(function () {
  'use strict';

  angular
    .module('crowdsource.list.controllers')
    .controller('ListController', ListController);

  ListController.$inject = ['$location', '$scope','$http'];

  /**
  * @namespace ListController
  */
  function ListController($location, $scope,$http) {
        $http.get("api-auth/v1/project/all/?format=json").success(function(data,config) {
        	$scope.projectlist = data;
        	console.log(data);
    });
  }
})();