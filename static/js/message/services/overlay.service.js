/**
 * Overlay
 * @namespace crowdsource.message.services
 */
(function () {
    'use strict';

    angular
        .module('crowdsource.message.services')
        .factory('Overlay', Overlay);

    Overlay.$inject = ['$cookies', '$http', '$q', 'HttpService'];

    /**
     * @namespace Overlay
     * @returns {Factory}
     */

    function Overlay($cookies, $http, $q, HttpService) {
        /**
         * @name Message
         * @desc The Factory to be returned
         */
        var Overlay = {
            recipient:null,
            isExpanded : false,
            isConnected : false
        };

        return Overlay;
    }
})();
