/**
* NavbarController
* @namespace crowdsource.layout.controllers
*/
(function () {
  'use strict';

  angular
    .module('crowdsource.layout.controllers')
    .controller('NavbarController', NavbarController);

  NavbarController.$inject = ['$scope', 'Authentication'];

  /**
  * @namespace NavbarController
  */
  function NavbarController($scope, Authentication) {
    var vm = this;

    vm.logout = logout;

    $scope.isLoggedIn = Authentication.isAuthenticated();

    /**
    * @name logout
    * @desc Log the user out
    * @memberOf crowdsource.layout.controllers.NavbarController
    */
    function logout() {
      Authentication.logout();
    }
  }
})();