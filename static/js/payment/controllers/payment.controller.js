(function () {
    'use strict';

    angular
        .module('crowdsource.payment.controllers')
        .controller('PaymentController', PaymentController);

    PaymentController.$inject = ['$state', '$timeout', '$mdToast', 'Payment', '$stateParams'];

    /**
     * @namespace PaymentController
     */
    function PaymentController($state, $timeout, $mdToast, Payment, $stateParams) {
        var self = this;

        activate();

        function activate() {

        }
    }
})();
