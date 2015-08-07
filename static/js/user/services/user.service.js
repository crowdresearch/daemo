/**
* User
* @namespace crowdsource.user.services
*/
(function () {
  'use strict';

  angular
    .module('crowdsource.user.services')
    .factory('User', User);

  User.$inject = ['$cookies', '$http', '$q', '$location', 'HttpService'];

  /**
  * @namespace User
  * @returns {Factory}
  */

  function User($cookies, $http, $q, $location, HttpService) {
    var User = {
      getProfile : getProfile
    };
    return User;

    function getProfile(profileid) {
      var settings = {
        url: '/api/profile/' + profileid + '/',
        method: 'GET'
      };
      return HttpService.doRequest(settings);
    }
  }

})();