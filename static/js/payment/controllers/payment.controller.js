(function () {
    'use strict';

    angular
        .module('crowdsource.payment.controllers')
        .controller('PaymentController', PaymentController);

    PaymentController.$inject = ['$state', '$timeout', '$mdToast', 'Payment', '$stateParams', 'User', '$location'];

    /**
     * @namespace PaymentController
     */
    function PaymentController($state, $timeout, $mdToast, Payment, $stateParams, User, $location) {
        var self = this;
        self.amount = 0;
        self.financial_data = null;
        self.credit_card = null;
        self.createCharge = createCharge;
        self.updateCreditCard = updateCreditCard;
        self.updateBank = updateBank;
        self.goTo = goTo;
        self.getTotal = getTotal;
        self.depositRequested = false;
        self.discount = 1.0;

        activate();
        function goTo(state) {
            $state.go(state);
        }

        function activate() {
            self.amount = $stateParams.suggestedAmount ? Math.ceil($stateParams.suggestedAmount) : null;
            User.getFinancialData().then(
                function success(response) {
                    self.financial_data = response[0];
                    if (self.financial_data.is_discount_eligible) {
                        self.discount = 0.5;
                    }
                },
                function error(response) {

                }
            );
        }

        function createCharge() {
            self.depositRequested = true;
            Payment.createCharge({"amount": self.amount}).then(
                function success(response) {
                    if ($stateParams.redirectTo) {
                        $location.search('redirectTo', null);
                        $location.search('suggestedAmount', null);
                        $location.path($stateParams.redirectTo);
                    }
                    else {
                        $state.go('profile');
                    }
                    self.depositRequested = false;
                },
                function error(response) {
                    self.depositRequested = false;
                    $mdToast.showSimple('Could not deposit funds.');
                }
            );
        }

        function updateCreditCard() {
            User.updateCreditCard(self.financial_data.default_card).then(
                function success(response) {
                    $state.go('profile');
                },
                function error(response) {
                    $mdToast.showSimple('Could update default credit card.');
                }
            );

        }

        function updateBank() {
            User.updateBankInfo(self.financial_data.default_bank).then(
                function success(response) {
                    $state.go('profile');
                },
                function error(response) {
                    $mdToast.showSimple('Could update default bank info.');
                }
            );

        }

        function getTotal() {
            return (self.amount * self.discount + 0.3) / 0.966;

            //x = y - 0.029 * y - 0.3 - 0.005*y
        }
    }
})();
