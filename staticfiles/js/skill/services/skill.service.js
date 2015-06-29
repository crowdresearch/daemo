/**
* Skill
* @namespace crowdsource.skill.services
*/
(function () {
  'use strict';

  angular
    .module('crowdsource.skill.services')
    .factory('Skill', Skill);

  Skill.$inject = ['$q'];

  /**
  * @namespace Skill
  * @returns {Factory}
  */

  function Skill($q) {
    var Skill = {
      getAllSkills: getAllSkills
    };

    function getAllSkills() {
      var deferred = $q.defer();
      deferred.resolve([
        'Data Entry',
        'Analysis',
        'Web Development',
        'Programming',
      ]);
      return deferred.promise;
    }


    return Skill;
  }

})();