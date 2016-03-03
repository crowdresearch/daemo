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
            var data = {
                paypal_id: $stateParams.paymentId,
                payer_id: $stateParams.PayerID,
                token: $stateParams.token
            };

            if (data.payer_id && data.payer_id && $state.current.name == 'payment_success') {
                Payment.execute(data).then(
                    function success(response) {
                        if (response.hasOwnProperty('message')) {
                            $mdToast.showSimple(response.message);
                        }
                    },
                    function error(response) {
                        if (response.hasOwnProperty('message')) {
                            $mdToast.showSimple(response.message);
                        } else {
                            $mdToast.showSimple("Payment failed");
                        }
                    }
                ).finally(function () {
                        $timeout(function () {
                            $state.go('profile');
                        }, 1000);
                    });
            }else{
                $timeout(function () {
                    $state.go('profile');
                }, 1000);
            }
        }
    }
})();
