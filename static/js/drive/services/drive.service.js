/**
* Drive
* @namespace crowdsource.drive.services
* @author dmorina
*/
(function () {
  'use strict';

  angular
    .module('crowdsource.drive.services')
    .factory('Drive', Drive);

  Drive.$inject = ['$cookies', '$http', '$q', 'HttpService'];

  /**
  * @namespace Drive
  * @returns {Factory}
  */

  function Drive($cookies, $http, $q, HttpService) {
    /**
    * @name Drive
    * @desc The Factory to be returned
    */
    var Drive = {
      addDriveAccount: addDriveAccount,
      finishAddDriveAccount: finishAddDriveAccount
    };
    return Drive;

    function addDriveAccount() {
      var settings = {
        url: '/api/google-drive/init/',
        method: 'POST'
      };
      return HttpService.doRequest(settings);
    }
    function finishAddDriveAccount(code) {
      var settings = {
        url: '/api/google-drive/finish/',
        data: {
            code: code
        },
        method: 'POST'
      };
      return HttpService.doRequest(settings);
    }
  }
})();
