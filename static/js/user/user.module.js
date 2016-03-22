(function () {
    'use strict';

    angular
        .module('crowdsource.user', [
            'crowdsource.user.controllers',
            'crowdsource.user.services'
        ]);

    angular
        .module('crowdsource.user.controllers', []);

    angular
        .module('crowdsource.user.services', ['ngCookies']);

})();
