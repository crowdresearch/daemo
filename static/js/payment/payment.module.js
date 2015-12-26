(function () {
    'use strict';

    angular
        .module('crowdsource.payment', [
            'crowdsource.payment.controllers',
            'crowdsource.payment.services'
    ]);

    angular
        .module('crowdsource.payment.controllers', []);
    angular
        .module('crowdsource.payment.services', []);
})();