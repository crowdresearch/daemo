(function () {
  'use strict';

  angular
    .module('crowdsource.skill', [
       'crowdsource.skill.services'
    ]);

  angular
    .module('crowdsource.skill.services', ['ngCookies']);

})();