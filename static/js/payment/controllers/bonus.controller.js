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
            self.requested = true;

            Payment.createBonus(worker).then(
                function success(response) {
                    $state.go('my_projects');

                },
                function error(response) {

                }
            );
        }

    }
})();
