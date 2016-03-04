(function () {
    'use strict';

    angular
        .module('crowdsource.rating.controllers')
        .controller('RatingController', RatingController);

    RatingController.$inject = ['$scope', '$log', '$mdToast', '$http', 'RatingService'];

    function RatingController($scope, $log, $mdToast, $http, RatingService) {

    }

})();