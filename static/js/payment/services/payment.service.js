
(function () {
    'use strict';

    angular
        .module('crowdsource.payment.services')
        .factory('Payment', Payment);

    Payment.$inject = ['$cookies', '$http', 'HttpService'];

    /**
     * @namespace Payment
     */

    function Payment($cookies, $http, HttpService) {
        /**
         * @name Payment
         * @desc The Factory to be returned
         */

        var Payment = {
            createCharge: createCharge,
            createBonus: createTransfer
        };

        return Payment;

        function createCharge(data) {
            var settings = {
                url: '/api/charges/',
                method: 'POST',
                data: data
            };
            return HttpService.doRequest(settings);
        }

        function createTransfer(data) {
            var settings = {
                url: '/api/transfers/bonus/',
                method: 'POST',
                data: data
            };
            return HttpService.doRequest(settings);
        }
    }
})();
