(function () {
    'use strict';

    angular
        .module('crowdsource.payment.controllers')
        .controller('PaymentController', PaymentController);

    PaymentController.$inject = ['$state', '$timeout', '$mdToast', 'Payment', '$stateParams', 'User'];

    /**
     * @namespace PaymentController
     */
    function PaymentController($state, $timeout, $mdToast, Payment, $stateParams, User) {
        var self = this;
        self.amount = 0;
        self.financial_data = null;
        self.credit_card = null;
        self.createCharge = createCharge;
        self.updateCreditCard = updateCreditCard;
        self.updateBank = updateBank;
        self.goTo = goTo;

        activate();
        function goTo(state) {
            $state.go(state);
        }

        function activate() {
            self.amount = $stateParams.suggestedAmount ? parseInt($stateParams.suggestedAmount) : null;
            User.getFinancialData().then(
                function success(response) {
                    self.financial_data = response[0];
                },
                function error(response) {

                }
            );
        }

        function createCharge() {
            Payment.createCharge({"amount": self.amount}).then(
                function success(response) {
                    $state.go('profile');
                },
                function error(response) {
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
    }
})();
