/**
 * Payment
 * @namespace crowdsource.payment.services
 * @author shirish
 */
(function () {
    'use strict';

    angular
        .module('crowdsource.payment.services')
        .factory('Payment', Payment);

    Payment.$inject = ['$cookies', '$http', '$q', 'HttpService', 'LocalStorage'];

    /**
     * @namespace Payment
     * @returns {Factory}
     */

    function Payment($cookies, $http, $q, HttpService, LocalStorage) {
        /**
         * @name Payment
         * @desc The Factory to be returned
         */

        var Payment = {
            create: create,
            execute: execute
        };

        return Payment;

        function create(data){
            var settings = {
                url: '/api/payment-paypal/',
                method: 'POST',
                data: data
            };
            return HttpService.doRequest(settings);
        }

        function execute(data) {
            var settings = {
                url: '/api/payment-paypal/execute/',
                method: 'POST',
                data:data
            };
            return HttpService.doRequest(settings);
        }
    }
})();
