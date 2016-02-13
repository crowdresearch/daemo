/**
 * AuthSettingsController
 * @namespace crowdsource.authentication.controllers
 */
(function () {
    'use strict';

    angular
        .module('crowdsource.authentication.controllers')
        .controller('AuthSettingsController', AuthSettingsController);

    AuthSettingsController.$inject = ['$window', '$location', '$scope', 'Authentication', '$mdToast', '$routeParams'];

    /**
     * @namespace AuthSettingsController
     */
    function AuthSettingsController($window, $location, $scope, Authentication, $mdToast, $routeParams) {
        var self = this;

        self.changePassword = changePassword;
        self.resetPassword = resetPassword;
        self.submitForgotPassword = submitForgotPassword;

        activate();
        function activate() {
            if (!Authentication.isAuthenticated() && $location.path().match(/change-password/gi)) {
                $location.url('/');
                return;
            }
            else if (Authentication.isAuthenticated() && !$location.path().match(/change-password/gi)) {
                $location.url('/');
                return;
            }
            if ($routeParams.activation_key) {
                Authentication.activate_account($routeParams.activation_key).then(function success(data, status) {
                    $location.url('/login');
                }, function error(data) {
                    self.error = data.data.message;
                    $mdToast.showSimple(data.data.message);
                }).finally(function () {
                });
            }
            else if ($routeParams.reset_key && $routeParams.enable==0) {
                Authentication.ignorePasswordReset($routeParams.reset_key).then(function success(data, status) {
                    $location.url('/');
                }, function error(data) {
                    self.error = data.data.message;
                    //$mdToast.showSimple(data.data.message);
                }).finally(function () {
                });
            }
        }

        /**
         * @name changePassword
         * @desc Change password of the user
         * @memberOf crowdsource.authentication.controllers.AuthSettingsController
         */
        function changePassword(isValid) {
            if(isValid){
                Authentication.changePassword(self.password, self.password1, self.password2).then(function success(data, status) {
                    $location.url('/profile');

                }, function error(data) {
                    if (data.data.hasOwnProperty('non_field_errors')) {
                        self.error = data.data['non_field_errors'].join(', ');
                    }
                    else {
                        self.error = data.data[0];
                    }
                    $scope.form.$setPristine();

                }).finally(function () {
                });
            }
            self.submitted=true;
        }

        /**
         * @name resetPassword
         * @desc Reset password of the user
         * @memberOf crowdsource.authentication.controllers.AuthSettingsController
         */
        function resetPassword() {
            Authentication.resetPassword($routeParams.reset_key, self.email, self.password).then(function success(data, status) {
                $location.url('/login');

            }, function error(data){
                self.error = data.data[0];
                $scope.form.$setPristine();

            }).finally(function () {
            });
        }
        /**
         * @name submitForgotPassword
         * @desc Send reset link
         * @memberOf crowdsource.authentication.controllers.AuthSettingsController
         */
        function submitForgotPassword(isValid) {
            if(isValid){
                Authentication.sendForgotPasswordRequest(self.email).then(function success(data, status) {
                    $mdToast.showSimple('Email with a reset link has been sent.');

                }, function error(data){
                    self.error = "Email not found";
                    $scope.form.$setPristine();

                }).finally(function () {
                });
            }
            self.submitted=true;
        }

    }
})();