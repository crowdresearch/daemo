/**
 * Register controller
 * @namespace crowdsource.authentication.controllers
 */
(function () {
    'use strict';

    angular
        .module('crowdsource.authentication.controllers', ['ngMaterial'])
        .controller('RegisterController', ['$location', '$scope', '$mdDialog', 'Authentication', 'cfpLoadingBar',
            function RegisterController($location, $scope, $mdDialog, Authentication, cfpLoadingBar) {

                activate();
                /**
                 * @name activate
                 * @desc Actions to be performed when this controller is instantiated
                 * @memberOf crowdsource.authentication.controllers.RegisterController
                 */
                function activate() {
                    // If the user is authenticated, they should not be here.
                    if (Authentication.isAuthenticated()) {
                        $location.url('/profile');
                    }
                }

                var vm = this;

                vm.register = register;
                vm.errors = [];

                /**
                 * @name register
                 * @desc Register a new user
                 * @memberOf crowdsource.authentication.controllers.RegisterController
                 */
                function register() {
                    cfpLoadingBar.start();
                    Authentication.register(vm.email, vm.firstname, vm.lastname,
                        vm.password1, vm.password2).then(function () {

                            showAlert();
                        }, function (data, status) {

                            //Global errors
                            if (data.data.hasOwnProperty('detail')) {
                                vm.error = data.data.detail;
                                $scope.form.$setPristine();
                            }

                            angular.forEach(data.data, function (errors, field) {

                                if (field == 'non_field_errors') {
                                    // Global errors
                                    vm.error = errors.join(', ');
                                    $scope.form.$setPristine();
                                } else {
                                    //Field level errors
                                    $scope.form[field].$setValidity('backend', false);
                                    $scope.form[field].$dirty = true;
                                    vm.errors[field] = errors.join(', ');
                                }
                            });

                        }).finally(function () {
                            cfpLoadingBar.complete();
                        });
                }

                /**
                 * @name showAlert
                 * @desc Alert a successful registration
                 * @memberOf crowdsource.authentication.controllers.RegisterController
                 */
                function showAlert() {
                  alert = $mdDialog.alert()
                    .title('Registration Successful')
                    .content('An activation mail has been sent to your email.'+
                        ' Please follow the instructions in the mail'+
                        ' to activate your account!')
                    .ok('Got it!');

                  $mdDialog
                      .show( alert )
                      .finally(function() {
                        alert = undefined;
                        $location.url('/login');
                      });
                }

            }]);
})();