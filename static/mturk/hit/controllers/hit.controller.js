(function () {
    'use strict';

    angular
        .module('mturk.hit.controllers', [])
        .controller('HITController', HITController);

    HITController.$inject = ['$scope', '$location', '$mdToast', 'HIT'];

    function HITController($scope, $location, $mdToast, HIT) {
        var self = this;

    }
})();


