/**
 * NavbarController
 * @namespace crowdsource.layout.controllers
 */
(function () {
    'use strict';

    angular
        .module('crowdsource.layout.controllers')
        .controller('NavbarController', NavbarController);

    NavbarController.$inject = ['$scope', '$rootScope', 'Authentication', 'User', '$mdSidenav',
        '$timeout', '$mdMedia', '$location'];

    /**
     * @namespace NavbarController
     */
    function NavbarController($scope, $rootScope, Authentication, User, $mdSidenav, $timeout, $mdMedia, $location) {
        var self = this;
        $scope.toggleRight = buildDelayedToggler('right');
        $scope.rightCtrl = rightCtrl;
        self.logout = logout;
        self.hasNewMessages = false;
        self.returned_tasks = 0;

        self.isLoggedIn = Authentication.isAuthenticated();
        // self.account = Authentication.getAuthenticatedAccount();
        self.profile = {};
        $rootScope.screenIsSmall = $mdMedia('sm');
        $rootScope.$mdMedia = $mdMedia;
        $rootScope.isSandboxEnvironment = $location.host().indexOf('sandbox') > -1;
        initializeWebSocket();
        getNotifications();
        getProfile();
        getPreferences();
        function initializeWebSocket() {
            $scope.$on('message', function (event, data) {
                // updateMessageStatus(true);
                if (data.hasOwnProperty('event') && data.event === 'TASK_RETURNED') {
                    getNotifications();
                }
            });
        }

        function updateMessageStatus(status) {
            if (status) {
                self.hasNewMessages = status;
            } else {
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


        function getProfile() {
            User.getProfile().then(
                function success(response) {
                    self.profile = response[0];
                },
                function error(response) {
                }
            ).finally(function () {
            });
        }

        function getPreferences() {
            User.getPreferences().then(
                function success(response) {
                    self.preferences = response[0];
                },
                function error(response) {
                }
            ).finally(function () {
            });
        }

        function debounce(func, wait, context) {
            var timer;

            return function debounced() {
                var context = $scope,
                    args = Array.prototype.slice.call(arguments);
                $timeout.cancel(timer);
                timer = $timeout(function () {
                    timer = undefined;
                    func.apply(context, args);
                }, wait || 10);
            };
        }

        function buildDelayedToggler(navID) {
            return debounce(function () {
                $mdSidenav(navID)
                    .toggle()
                    .then(function () {
                        //$log.debug("toggle " + navID + " is done");
                    });
            }, 200);
        }

        function rightCtrl($scope, $timeout, $mdSidenav, $log) {
            $scope.close = function () {
                $mdSidenav('right').close()
                    .then(function () {
                        //$log.debug("close RIGHT is done");
                    });
            };

        }

    }
})();
