/**
 * LoginController
 * @namespace crowdsource.authentication.controllers
 */
(function () {
    'use strict';

    angular
        .module('crowdsource.authentication.controllers')
        .controller('LoginController', LoginController);

    LoginController.$inject = ['$window', '$location', '$state', '$stateParams', '$scope', '$rootScope', 'Authentication'];

    /**
     * @namespace LoginController
     */
    function LoginController($window, $location, $state, $stateParams, $scope, $rootScope, Authentication) {
        var vm = this;

        vm.login = login;
        vm.Authentication = Authentication;

        activate();

        /**
         * @name activate
         * @desc Actions to be performed when this controller is instantiated
         * @memberOf crowdsource.authentication.controllers.LoginController
         */
        function activate() {


            // If the user is authenticated, they should not be here.
            if (Authentication.isAuthenticated()) {
                gotoNext();
            }
        }

        /**
         * @name login
         * @desc Log the user in
         * @memberOf crowdsource.authentication.controllers.LoginController
         */
        function login(isValid) {
            if (isValid) {
                Authentication.login(vm.username, vm.password).then(function success(data, status) {

                    //var user = {username: data.data.username, password: vm.password};
                    //OAuth.getAccessToken(user, null, post_config);
                    //TODO configure OAuthProvider Here so that we can set client secret and client id
                    // will be replaced by OAuth above
                    Authentication.setAuthenticatedAccount(data.data);

                    $scope.$watch(Authentication.isAuthenticated, function (newValue, oldValue) {
                        if (newValue) {
                            $rootScope.initializeWebSocket();
                            gotoNext();
                        }
                    });

                    /*Authentication.getOauth2Token(data.data.username, vm.password,
                     "password", data.data.client_id, data.data.client_secret).then(function success(data, status) {
                     Authentication.setOauth2Token(data.data);
                     $window.location = '/profile'
                     }, function error(data, status) {
                     vm.error = data.data.detail;
                     $scope.loginForm.$setPristine();
                     }); */
                }, function error(data, status) {
                    vm.error = data.data.detail;
                    $scope.loginForm.$setPristine();

                }).finally(function () {
                });
            }
            vm.submitted = true;
        }

        function gotoNext() {
            var next = $stateParams.next;
            var account = Authentication.getAuthenticatedAccount();

            if (next != null) {
                $location.url(next);
            } else {
                if (account.is_worker){
                    $state.go('task_feed');
                }
                else {
                    $state.go('my_projects');
                }

            }
        }
    }
})();
