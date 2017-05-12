/**
 * LoginController
 * @namespace crowdsource.authentication.controllers
 */
(function () {
    'use strict';

    angular
        .module('crowdsource.authentication.controllers')
        .controller('LogoutController', LogoutController);

    LogoutController.$inject = ['$window', '$location', '$state', '$stateParams', '$scope', '$rootScope', 'Authentication'];

    /**
     * @namespace LoginController
     */
    function LogoutController($window, $location, $state, $stateParams, $scope, $rootScope, Authentication) {
        var vm = this;

        $rootScope.closeWebSocket();
        Authentication.logout();
    }
})();
