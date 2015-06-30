/**
* Worker
* @namespace crowdsource.worker.services
*/
(function () {
  'use strict';

  angular
    .module('crowdsource.worker.services')
    .factory('Worker', Worker);

  Worker.$inject = ['$cookies', '$http', '$q', '$location', 'HttpService'];

  /**
  * @namespace Worker
  * @returns {Factory}
  */

  function Worker($cookies, $http, $q, $location, HttpService) {
    var Worker = {
      getWorkerPrivateProfile: getWorkerPrivateProfile,
      getWorkerTaskPortfolio : getWorkerTaskPortfolio,
      addSkill: addSkill,
      removeSkill: removeSkill
    };

    return Worker;

    function getWorkerPrivateProfile(profileid) {
      var settings = {
        url: '/api/worker/' + profileid + '/',
        method: 'GET'
      };
      return HttpService.doRequest(settings);
    }   

    function getWorkerTaskPortfolio() {
      return $http({
        url: 'https://api.myjson.com/bins/q7jc',
        method: 'GET'
      });
    }

    function addSkill(worker) {
      var settings = {
        url: '/api/worker/',
        method: 'POST',
        data: worker
      };
      return HttpService.doRequest(settings);
    }

    function removeSkill(workerId, skillId) {
     var settings = {
        url: '/api/worker-skill/',
        method: 'DELETE',
        data: {
          worker_id: workerId,
          skill: skillId
        }
      };
      return HttpService.doRequest(settings); 
    }
  }

})();