/**
* NavbarController
* @namespace crowdsource.layout.controllers
*/
(function () {
  'use strict';

  angular
    .module('crowdsource.layout.controllers')
    .controller('NavbarController', NavbarController);

  NavbarController.$inject = ['$scope', '$rootScope', 'Authentication'];

  /**
  * @namespace NavbarController
  */
  function NavbarController($scope, $rootScope, Authentication) {
    var vm = this;

    vm.logout = logout;

    $rootScope.isLoggedIn = Authentication.isAuthenticated();
    $rootScope.account = Authentication.getAuthenticatedAccount();
    console.log($rootScope.account);

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