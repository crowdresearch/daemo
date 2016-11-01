/**
 * Date: 1/9/15
 * Author: Shirish Goyal
 */

(function () {
    'use strict';

    angular
        .module('crowdsource.interceptor', [])
        .factory('AuthHttpResponseInterceptor', AuthHttpResponseInterceptor);

    AuthHttpResponseInterceptor.$inject = ['$log', '$injector', '$q'];

    function AuthHttpResponseInterceptor($log, $injector, $q) {
        return {
            responseError: function (rejection) {
                var $http = $injector.get('$http');
                var $state = $injector.get('$state');
                if (rejection.status === 403) {
                    if (rejection.hasOwnProperty('data')
                        && rejection.data.hasOwnProperty('detail')
                        && (rejection.data.detail.indexOf("Authentication credentials were not provided") != -1)
                    ) {
                        var Authentication = $injector.get('Authentication');
                        Authentication.unauthenticate();
                        $state.transitionTo('auth.login');
                    }
                }

                if (rejection.status === 400) {
                    if (rejection.hasOwnProperty('data')
                        && rejection.data.hasOwnProperty('message')
                        && (rejection.data.message == 'MISSING_USER_INFORMATION')
                    ) {
                        $state.transitionTo('getting_started');

                    }
                }

                return $q.reject(rejection);
            }
        }
    }

})();
