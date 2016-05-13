/**
 * PreferencesController
 * @namespace crowdsource.user.controllers
 */
(function () {
    'use strict';

    angular
        .module('crowdsource.user.controllers')
        .controller('PreferencesController', PreferencesController);

    PreferencesController.$inject = ['$state', '$scope', '$window', '$mdToast', 'User'];

    /**
     * @namespace PreferencesController
     */
    function PreferencesController($state, $scope, $window, $mdToast, User) {
        var self = this;

        function activate() {
            
        }
    }
})();
