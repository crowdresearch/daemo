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
            Authentication.login(self.password, self.password1).then(function success(data, status) {


            }, function error(data, status) {
                self.error = data.data.detail;
                $scope.form.$setPristine();

            }).finally(function () {
            });
        }
    }
})();