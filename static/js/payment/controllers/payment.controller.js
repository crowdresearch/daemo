(function () {
    'use strict';

    angular
        .module('crowdsource.payment.controllers')
        .controller('PaymentController', PaymentController);

    PaymentController.$inject = ['$location', '$timeout', '$mdToast', 'Payment', '$routeParams'];

    /**
     * @namespace PaymentController
     */
    function PaymentController($location, $timeout, $mdToast, Payment, $routeParams) {
        var self = this;
        activate();

        function activate() {
            var data = {
                paypal_id: $routeParams.paymentId,
                payer_id: $routeParams.PayerID,
                token: $routeParams.token
            };

            if (data.payer_id && data.payer_id && $location.path() == '/payment-success') {
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
                            $location.url('/profile');
                        }, 1000);
                    });
            }else{
                $timeout(function () {
                    $location.url('/profile');
                }, 1000);
            }
        }
    }
})();
