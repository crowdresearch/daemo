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

        self.isLoggedIn = Authentication.isAuthenticated();
        self.account = Authentication.getAuthenticatedAccount();

        getProfile();
        initializeWebSocket();

        function getProfile() {
            User.getProfile(self.account.username)
                .then(function (data) {
                    var profile = data[0];

                    if (profile.hasOwnProperty('worker')) {
                        self.account.worker = profile.worker;
                        self.account.worker.level_text = '(Level ' + profile.worker.level + ')';

                    }
                });
        }

        function initializeWebSocket() {
            $scope.$on('message', function (event, data) {
                updateMessageStatus(true);
            });

            $scope.$on('notification', function (event, data) {
                notification(data);
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

        function notification(data){
            if(data.hasOwnProperty('level')) {
                getProfile();
            }
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
