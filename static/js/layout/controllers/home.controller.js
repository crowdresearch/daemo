/**
 * HomeController
 * @namespace crowdsource.layout.controllers
 */
(function () {
    'use strict';

    angular
        .module('crowdsource.layout.controllers')
        .controller('HomeController', HomeController);

    HomeController.$inject = ['$scope', '$rootScope', 'Authentication'];

    /**
     * @namespace HomeController
     */
    function HomeController($scope, $rootScope, Authentication) {
        var self = this;

        self.logout = logout;

        $scope.isLoggedIn = Authentication.isAuthenticated();
        $scope.account = Authentication.getAuthenticatedAccount();

        /**
         * @name logout
         * @desc Log the user out
         * @memberOf crowdsource.layout.controllers.HomeController
         */
        function logout() {
            $rootScope.closeWebSocket();

            Authentication.logout();
        }
    }
})();
