/**
 * NavbarController
 * @namespace crowdsource.layout.controllers
 */
(function () {
    'use strict';

    angular
        .module('crowdsource.layout.controllers')
        .controller('NavbarController', NavbarController);

    NavbarController.$inject = ['$scope', '$rootScope', 'Authentication', 'User'];

    /**
     * @namespace NavbarController
     */
    function NavbarController($scope, $rootScope, Authentication, User) {
        var self = this;

        self.logout = logout;
        self.hasNewMessages = false;
        self.returned_tasks = 0;

        self.isLoggedIn = Authentication.isAuthenticated();
        self.account = Authentication.getAuthenticatedAccount();

        initializeWebSocket();
        getNotifications();
        function initializeWebSocket() {
            $scope.$on('message', function (event, data) {
                // updateMessageStatus(true);
                if(data.hasOwnProperty('event') && data.event === 'TASK_RETURNED' ){
                    getNotifications();
                }
            });
        }

        function updateMessageStatus(status){
            if(status)
            {
                self.hasNewMessages = status;
            }else{
                // TODO: handle logic
            }
        }
        function getNotifications() {
            User.getNotifications().then(
                function success(response) {
                   self.returned_tasks = response[0].returned_tasks;
                },
                function error(response) {
                }
            ).finally(function () {
            });
        }

        /**
         * @name logout
         * @desc Log the user out
         * @memberOf crowdsource.layout.controllers.NavbarController
         */
        function logout() {
            $rootScope.closeWebSocket();
            Authentication.logout();
        }


    }
})();
