/**
* Register page 2 controller
* @namespace crowdsource.authentication.controllers
*/
(function () {
  'use strict';

  var myapp = angular.module('crowdsource.authentication.controllers');
  myapp.controller('Registerpage2Controller', ['$location', '$scope', 'Authentication', 'cfpLoadingBar', '$alert',
      function Registerpage2Controller($location, $scope, Authentication, cfpLoadingBar, $alert) {

        activate();
        /**
         * @name activate
         * @desc Actions to be performed when this controller is instantiated
         * @memberOf crowdsource.authentication.controllers.Registerpage2Controller
         */
        function activate() {
          // If the user is authenticated, they should not be here.
          if (Authentication.isAuthenticated()) {
            $location.url('/home');
          }
        }
        var vm = this;

        vm.registerstep2 =registerstep2;
	
        /**
        * @name register
        * @desc Register a new user
        * @memberOf crowdsource.authentication.controllers.Registerpage2Controller
        */
        function registerstep2() {
          cfpLoadingBar.start();
	
	 $location.url('/success_reg')
        }
    }]);
})();
