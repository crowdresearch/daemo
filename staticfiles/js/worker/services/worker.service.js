/**
* Worker
* @namespace crowdsource.worker.services
*/
(function () {
  'use strict';

  angular
    .module('crowdsource.worker.services')
    .factory('Worker', Worker);

  Worker.$inject = ['$cookies', '$http', '$q', '$location'];

  /**
  * @namespace Worker
  * @returns {Factory}
  */

  function Worker($cookies, $http, $q, $location) {
    var Worker = {
      getWorkerPrivateProfile: getWorkerPrivateProfile,
      getWorkerTaskPortfolio : getWorkerTaskPortfolio
    };

    return Worker;

    function getWorkerPrivateProfile() {
      return $http({
        url: 'http://share-quick.com/cr/getWorkerProfile.php',
        method: 'POST'
      });
      
    }   

    function getWorkerTaskPortfolio() {
      return $http({
        url: 'https://api.myjson.com/bins/q7jc',
        method: 'GET'
      });
   }         

    
  }
})();