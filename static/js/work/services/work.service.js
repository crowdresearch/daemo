/**
* WorkService
* @namespace crowdsource.work.services
*/
(function () {
  'use strict';

  angular
    .module('crowdsource.work.services')
    .factory('WorkService', WorkService);

  WorkService.$inject = ['$cookies', '$q', '$location', 'HttpService'];

  /**
  * @namespace WorkService
  * @returns {Factory}
  */

  function WorkService($cookies, $q, $location, HttpService) {
    var WorkService = {
      removeFile: removeFile
    };

    return WorkService;

    function removeFile(fileId) {
     var settings = {
        url: '/api/requesterinputfile/' + fileId + '/',
        method: 'DELETE'
      };
      return HttpService.doRequest(settings); 
    }

  }
  
})();