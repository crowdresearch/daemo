/**
* Requester
* @namespace crowdsource.requester.services
*/
(function () {
  'use strict';

  angular
    .module('crowdsource.requester.services')
    .factory('Requester', Requester);

  Requester.$inject = ['$cookies', '$http', '$q', '$location'];

  /**
  * @namespace Requester
  * @returns {Factory}
  */

  function Requester($cookies, $http, $q, $location) {
    /**
    * @name Requester
    * @desc The Factory to be returned
    */
    var Requester = {
      getRequesterPrivateProfile: getRequesterPrivateProfile
    };

    return Requester;

    function getRequesterPrivateProfile() {
      return $http({
        url: 'http://share-quick.com/cr/getRequester.php',
        method: 'POST'
      });
    }            
    
  }
})();