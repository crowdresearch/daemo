/**
 * UserController
 * @namespace crowdsource.user.controllers
 */
(function () {
    'use strict';

    angular
        .module('crowdsource.user.controllers')
        .controller('UserController', UserController);

    UserController.$inject = ['$location', '$scope',
        '$routeParams', '$mdToast', 'Authentication', 'User', 'Skill'];

    /**
     * @namespace UserController
     */
    function UserController($location, $scope,
                            $routeParams, $mdToast, Authentication, User) {

        var self = this;
        var userAccount = Authentication.getAuthenticatedAccount();

    }
})();