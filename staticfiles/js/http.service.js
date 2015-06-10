/**
* Http service master.
* @namespace crowdsource.services
*/
(function () {
  'use strict';

  angular
    .module('crowdsource.services', [])
    .factory('HttpService', HttpService);

  HttpService.$inject = ['$cookies', '$http', '$q', '$location', 'Authentication'];

  /**
  * @namespace HttpService
  * @returns {Factory}
  */

  function HttpService($cookies, $http, $q, $location, Authentication) {
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
      Authentication.attachHeaderTokens(settings);

      $http(settings).success(function (data,config) {
        deferred.resolve(arguments);
      }).error(function (data, status, headers, config) {
        deferred.reject(arguments);
        // Handle authorization error, redirect to login.
        if (status === 403) {
          Authentication.unauthenticate();
          Authentication.setOauth2Token();
          window.location = '/login';
        }
      });
      return deferred.promise;
    }

  }
})();