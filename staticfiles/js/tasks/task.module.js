(function () {
  'use strict';

  angular
    .module('crowdsource.tasks', [
      'crowdsource.tasks.controllers',
          'crowdsource.task.services'
    ]);

  angular
    .module('crowdsource.tasks.controllers', []);
  angular
    .module('crowdsource.tasks.services', []);
})();
