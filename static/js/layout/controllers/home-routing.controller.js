/**
 * HomeRoutingController
 * @namespace crowdsource.layout.controllers
 */
(function () {
    'use strict';

    angular
        .module('crowdsource.layout.controllers')
        .controller('HomeRoutingController', HomeRoutingController);

    HomeRoutingController.$inject = ['$scope', '$rootScope', '$state', 'Authentication'];

    /**
     * @namespace HomeRoutingController
     */
    function HomeRoutingController($scope, $rootScope, $state, Authentication) {
        var self = this;

        $scope.isLoggedIn = Authentication.isAuthenticated();
        $scope.account = Authentication.getAuthenticatedAccount();

        activate();

        function activate() {
            if(!$scope.isLoggedIn){
                goTo('home');
            }
            else {
                if($scope.account.is_worker){
                    goTo("task_feed");
                }
                else {
                    goTo("my_projects");
                }
            }
        }

        function goTo(state) {
            $state.go(state);
        }
    }
})();
