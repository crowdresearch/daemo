/**
* Http service master.
* @namespace crowdsource.services
*/
(function () {
  'use strict';

  angular
    .module('crowdsource.services', [])
    .factory('HttpService', HttpService);

  HttpService.$inject = ['$cookies', '$http', '$q', '$location', '$window', 'Authentication'];

  /**
  * @namespace HttpService
  * @returns {Factory}
  */

  function HttpService($cookies, $http, $q, $location, $window, Authentication) {
    /**
    * @name HttpService
    * @desc The Factory to be returned
    */
    var HttpService = {
      doRequest: doRequest
    };

    return HttpService;


    /**
    * @name doRequest
    * @desc Performs a given request.
    * @returns {Promise}
    * @memberOf crowdsource.tasksearch.services.HttpService
    */
    function doRequest(settings) {
      
      var deferred = $q.defer();
      //Authentication.attachHeaderTokens(settings); // until we write OAUTH2 encryption middleware

      $http(settings).success(function (data, status, headers, config) {
        deferred.resolve(arguments);
      }).error(function (data, status, headers, config) {
        deferred.reject(arguments);
        // Handle authorization error, redirect to login.
        /*
          if ((status === 403 || status === 401) && data.error === 'invalid_token') {
          Authentication.getRefreshToken()
            .then(function success(data, status) {

              Authentication.setOauth2Token(data.data);
              $window.location.reload();
          
            }, function error(data, status) {

              Authentication.unauthenticate();
              $window.location = '/login';
          
            });
        } else {
          deferred.reject(arguments);
        }
        */
      });
      return deferred.promise;
    }
  }
})();