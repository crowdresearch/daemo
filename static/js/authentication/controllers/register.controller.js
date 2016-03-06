/**
 * Register controller
 * @namespace crowdsource.authentication.controllers
 */
(function () {
    'use strict';

    angular
        .module('crowdsource.authentication.controllers')
        .controller('RegisterController', ['$state', '$scope', 'Authentication', 'cfpLoadingBar', '$mdToast',
            function RegisterController($state, $scope, Authentication, cfpLoadingBar, $mdToast) {

                activate();
                /**
                 * @name activate
                 * @desc Actions to be performed when this controller is instantiated
                 * @memberOf crowdsource.authentication.controllers.RegisterController
                 */
                function activate() {
                    // If the user is authenticated, they should not be here.
                    if (Authentication.isAuthenticated()) {
                        $state.go('profile');
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
                function register(isValid) {
                    if (isValid) {
                        cfpLoadingBar.start();
                        Authentication.register(vm.email, vm.firstname, vm.lastname,
                            vm.password1, vm.password2).then(function () {

                                $state.go('login');
                                $mdToast.showSimple('Email with an activation link has been sent.');
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
                    vm.submitted = true;
                }
            }]);
})();