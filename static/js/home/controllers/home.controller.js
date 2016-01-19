/**
 * HomeController
 * @namespace crowdsource.home.controllers
 */
(function () {
    'use strict';

    angular
        .module('crowdsource.home.controllers')
        .controller('HomeController', HomeController);

    HomeController.$inject = ['$location', '$scope', 'Authentication', '$mdSidenav', '$mdUtil', '$mdMedia'];

    /**
     * @namespace HomeController
     */
    function HomeController($location, $scope, Authentication, $mdSidenav, $mdUtil, $mdMedia) {
        var self = this;
        self.navigateTo = navigateTo;
        self.sideNavToggler = sideNavToggler;
        self.toggleLeft = sideNavToggler('left');
        self.toggleRight = sideNavToggler('right');
        self.getLocation = getLocation;
        self.logout = logout;
        $scope.$mdMedia = $mdMedia;
        function sideNavToggler(navID) {
            var debounceFn = $mdUtil.debounce(function () {
                $mdSidenav(navID)
                    .toggle()
                    .then(function () {
                    });
            }, 300);
            return debounceFn;
        }

        function navigateTo(target) {
            $location.path('/' + target);
        }

        function getLocation() {
            return $location.path();
        }

        function logout() {
            Authentication.logout();
        }
    }
})();
