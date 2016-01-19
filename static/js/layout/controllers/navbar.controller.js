/**
 * NavbarController
 * @namespace crowdsource.layout.controllers
 */
(function () {
    'use strict';

    angular
        .module('crowdsource.layout.controllers')
        .controller('NavbarController', NavbarController);

    NavbarController.$inject = ['$scope', '$rootScope', 'Authentication', '$location'];

    /**
     * @namespace NavbarController
     */
    function NavbarController($scope, $rootScope, Authentication, $location) {
        var self = this;

        self.logout = logout;
        $rootScope.isActiveTab = isActiveTab;
        $rootScope.isLoggedIn = Authentication.isAuthenticated();
        $rootScope.account = Authentication.getAuthenticatedAccount();

        /**
         * @name logout
         * @desc Log the user out
         * @memberOf crowdsource.layout.controllers.NavbarController
         */
        function logout() {
            Authentication.logout();
        }

        function isActiveTab(path) {
            var re = new RegExp();
            re = path == 'my-projects' ? new RegExp(/(my-projects|project-review|create-project)/gi) : new RegExp(path, 'gi');
            return ($location.path().match(re));
        }
    }
})();
