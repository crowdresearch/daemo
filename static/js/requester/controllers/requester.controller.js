/**
 * RequesterProfileController
 * @namespace crowdsource.requester.controllers
 */
(function () {
    'use strict';

    angular
        .module('crowdsource.requester.controllers')
        .controller('RequesterProfileController', RequesterProfileController);

    RequesterProfileController.$inject = ['$state', '$scope', 'Authentication', 'Requester'];

    /**
     * @namespace RequesterProfileController
     */
    function RequesterProfileController($state, $scope, Authentication, Requester) {
        var vm = this;

        Requester.getRequesterPrivateProfile().success(function (data) {
            $scope.requesterProfile = data;
        });

        Requester.getRequesterTaskPortfolio().success(function (data) {
            $scope.requesterTaskPortfolio = data;


            $scope.getRate = function (num, totalSubmissions) {
                var rate = (parseInt((num) / (totalSubmissions) * 100).toFixed(2));
                return rate;

            };

            $scope.range = new Array(5);
            $scope.convertToInt = function (value) {
                return parseInt(value);
            };
        });
    }
})();
