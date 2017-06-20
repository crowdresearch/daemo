(function () {
    'use strict';

    angular
        .module('crowdsource.payment.controllers')
        .controller('BonusController', BonusController);

    BonusController.$inject = ['$state', '$timeout', '$mdToast', 'Payment', '$stateParams', 'User', '$location'];

    /**
     * @namespace BonusController
     */
    function BonusController($state, $timeout, $mdToast, Payment, $stateParams, User, $location) {
        var self = this;
        self.amount = 1;
        self.financial_data = null;
        self.requested = false;
        self.handle = null;
        self.reason = null;
        self.complete = false;
        self.createBonus = createBonus;

        self.goTo = goTo;


        activate();
        function goTo(state) {
            $state.go(state);
        }

        function activate() {
            self.handle = $stateParams.handle;

            User.getFinancialData().then(
                function success(response) {
                    self.financial_data = response[0];

                },
                function error(response) {

                }
            );
        }

        function createBonus() {

            var bonus = {
                "handle": self.handle,
                "amount": self.amount,
                "reason": self.reason
            };

            if(!self.reason){
                $mdToast.showSimple('Reason is required.');
                return;
            }
            self.requested = true;
            Payment.createBonus(bonus).then(
                function success(response) {
                    self.requested = false;
                    self.complete = true;


                },
                function error(response) {
                    self.requested = false;
                    $mdToast.showSimple(response[0].message);
                }
            );
        }

    }
})();
