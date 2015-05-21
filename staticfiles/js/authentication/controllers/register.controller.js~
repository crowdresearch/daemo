/**
* Register controller
* @namespace crowdsource.authentication.controllers
*/
(function () {
  'use strict';

  var myapp = angular.module('crowdsource.authentication.controllers', []);
  myapp.controller('RegisterController', ['$location', '$scope', 'Authentication', 'cfpLoadingBar', '$alert',
      function RegisterController($location, $scope, Authentication, cfpLoadingBar, $alert) {

        activate();
        /**
         * @name activate
         * @desc Actions to be performed when this controller is instantiated
         * @memberOf crowdsource.authentication.controllers.RegisterController
         */
        function activate() {
          // If the user is authenticated, they should not be here.
          if (Authentication.isAuthenticated()) {
            $location.url('/home');
          }
        }
        var vm = this;

        vm.register = register;
	vm.country = 'country';

        /**
        * @name register
        * @desc Register a new user
        * @memberOf crowdsource.authentication.controllers.RegisterController
        */
        function register() {
          cfpLoadingBar.start();

          Authentication.register(vm.email, vm.firstname, vm.lastname,
            vm.password1, vm.password2).then(function () {
              console.log("Done")
              $location.url('/registerstep2');
            }, function (data, status) {
              $alert({
                title: 'Erro',
                content: data.data.message,
                placement: 'top',
                type: 'danger',
                keyboard: true,
                duration: 5});
            }).finally(function () {
              cfpLoadingBar.complete();

            });
        }
    }]);
})();
