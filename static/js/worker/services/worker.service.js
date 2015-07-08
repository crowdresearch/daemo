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

    function getWorkerPrivateProfile(username) {
      var settings = {
        url: '/api/worker/' + username + '/',
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

    function addSkill(skillId) {
      var settings = {
        url: '/api/worker-skill/',
        method: 'POST',
        data: {
          skill: skillId
        }
      };
      return HttpService.doRequest(settings);
    }

    function removeSkill(skillId) {
     var settings = {
        url: '/api/worker-skill/' + skillId + '/',
        method: 'DELETE'
      };
      return HttpService.doRequest(settings); 
    }
  }

})();