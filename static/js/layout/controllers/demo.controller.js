/**
 * DemoController
 * @namespace crowdsource.layout.controllers
 */
(function () {
    'use strict';

    angular
        .module('crowdsource.layout.controllers')
        .controller('DemoController', DemoController);

    DemoController.$inject = ['$scope', '$rootScope', '$state', '$anchorScroll', 'Authentication'];

    /**
     * @namespace DemoController
     */
    function DemoController($scope, $rootScope, $state, $anchorScroll, Authentication) {
        var self = this;

        self.logout = logout;
        self.scrollTo = scrollTo;
        self.goTo = goTo;

        $scope.isLoggedIn = Authentication.isAuthenticated();
        $scope.account = Authentication.getAuthenticatedAccount();

        /**
         * @name logout
         * @desc Log the user out
         * @memberOf crowdsource.layout.controllers.DemoController
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
