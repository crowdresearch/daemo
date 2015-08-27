/**
 * AuthSettingsController
 * @namespace crowdsource.authentication.controllers
 */
(function () {
    'use strict';

    angular
        .module('crowdsource.authentication.controllers')
        .controller('AuthSettingsController', AuthSettingsController);

    AuthSettingsController.$inject = ['$window', '$location', '$scope', 'Authentication'];

    /**
     * @namespace AuthSettingsController
     */
    function AuthSettingsController($window, $location, $scope, Authentication) {
        var self = this;

        self.changePassword = changePassword;

        activate();
        function activate() {
            if (!Authentication.isAuthenticated()) {
                $location.url('/');
            }
        }

        /**
         * @name changePassword
         * @desc Change password of the user
         * @memberOf crowdsource.authentication.controllers.AuthSettingsController
         */
        function changePassword() {
            if(self.password1!==self.password2){
                self.error = 'Passwords do not match';
                $scope.form.$setPristine();
                return;
            }
            Authentication.changePassword(self.password, self.password1, self.password2).then(function success(data, status) {
                $location.url('/profile');

            }, function error(data) {
                self.error = data.data[0];
                $scope.form.$setPristine();

            }).finally(function () {
            });
        }
    }
})();