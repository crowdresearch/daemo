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
        var self = this;

        self.logout = logout;

        $scope.isLoggedIn = Authentication.isAuthenticated();
        $scope.account = Authentication.getAuthenticatedAccount();

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
