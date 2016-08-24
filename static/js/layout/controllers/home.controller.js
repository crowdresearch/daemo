/**
 * HomeController
 * @namespace crowdsource.layout.controllers
 */
(function () {
    'use strict';

    angular
        .module('crowdsource.layout.controllers')
        .controller('HomeController', HomeController);

    HomeController.$inject = ['$scope', '$rootScope', '$state', '$anchorScroll', 'Authentication'];

    /**
     * @namespace HomeController
     */
    function HomeController($scope, $rootScope, $state, $anchorScroll, Authentication) {
        var self = this;

        self.logout = logout;
        self.scrollTo = scrollTo;

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

        function goTo(state){
            $state.go(state);
        }
    }
})();
