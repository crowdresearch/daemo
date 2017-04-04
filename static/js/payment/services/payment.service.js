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
     */

    function Payment($cookies, $http, $q, HttpService, LocalStorage) {
        /**
         * @name Payment
         * @desc The Factory to be returned
         */

        var Payment = {
            createCharge: createCharge
        };

        return Payment;

        function createCharge(data){
            var settings = {
                url: '/api/charges/',
                method: 'POST',
                data: data
            };
            return HttpService.doRequest(settings);
        }
    }
})();
