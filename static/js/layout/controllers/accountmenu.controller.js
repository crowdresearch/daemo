/**
* AccountMenuController
* @namespace crowdsource.layout.controllers
*/
(function () {
  'use strict';

  angular
    .module('crowdsource.layout.controllers')
    .controller('AccountMenuController', AccountMenuController);

  AccountMenuController.$inject = ['$scope', '$rootScope', '$location'];

  /**
  * @namespace AccountMenuController
  */
  function AccountMenuController($scope, $rootScope, $location) {
    var vm = this;
    
    $scope.getClass = function(path) {
      var locationPath = $location.path().split('/');
      path = path.split('/');
      if (locationPath[locationPath.length - 1] === path[path.length - 1]) {
        return "active"
      } else {
        return ""
      }
    };
  }
})();