/**
* Register controller
* @namespace crowdsource.authentication.controllers
*/
(function () {
  'use strict';

  angular
    .module('crowdsource.authentication.controllers')
    .controller('RegisterController', ['$location', '$scope', 'Authentication',  
      function RegisterController($location, $scope, Authentication) {

        activate();

        /**
         * @name activate
         * @desc Actions to be performed when this controller is instantiated
         * @memberOf crowdsource.authentication.controllers.RegisterController
         */
        function activate() {
          // If the user is authenticated, they should not be here.
          if (Authentication.isAuthenticated()) {
            $location.url('/');
          }
        }
        var vm = this;

        vm.register = register;

        /**
        * @name register
        * @desc Register a new user
        * @memberOf crowdsource.authentication.controllers.RegisterController
        */
        function register() {
          Authentication.register(vm.email, vm.firstname, vm.lastname,
            vm.password1, vm.password2);
        }
    }]);
})();