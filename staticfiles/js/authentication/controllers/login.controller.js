/**
* LoginController
* @namespace crowdsource.authentication.controllers
*/
(function () {
  'use strict';

  angular
    .module('crowdsource.authentication.controllers')
    .controller('LoginController', LoginController);

  LoginController.$inject = ['$window', '$location', '$scope', 'Authentication', 'cfpLoadingBar', '$alert',];

  /**
  * @namespace LoginController
  */
  function LoginController($window, $location, $scope, Authentication, cfpLoadingBar, $alert) {
    var vm = this;

    vm.login = login;

    activate();

    /**
    * @name activate
    * @desc Actions to be performed when this controller is instantiated
    * @memberOf crowdsource.authentication.controllers.LoginController
    */
    function activate() {
      // If the user is authenticated, they should not be here.
      if (Authentication.isAuthenticated()) {
        $location.url('/');
      }
    }

    /**
    * @name login
    * @desc Log the user in
    * @memberOf crowdsource.authentication.controllers.LoginController
    */
    function login() {
      cfpLoadingBar.start();
      
      Authentication.login(vm.email, vm.password).then(function success(data, status) {
      
        Authentication.setAuthenticatedAccount(data.data);
        $window.location = '/'
      
      }, function error(data, status) {
      
        $alert({
          title: 'Error logging in!',
          content: data.data.message,
          placement: 'top',
          type: 'danger',
          keyboard: true,
          duration: 5});
      
      }).finally(function () {
        cfpLoadingBar.complete();
      });
    }
  }
})();