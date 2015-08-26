/**
* ModuleCacheService
* @namespace crowdsource.tasks.services
*/
(function () {
  'use strict';

  angular
    .module('crowdsource.task.services')
    .factory('ModuleCacheService', ModuleCacheService);

  ModuleCacheService.$inject = ['$cookies', '$q', '$location', 'HttpService'];

  /**
  * @namespace ModuleCacheService
  * @returns {Factory}
  */

  function ModuleCacheService($cookies, $q, $location, HttpService) {
    /**
    * @name ModuleCacheService
    * @desc Keeps an instance of the module to be retrieved and used as needed.
    */
    var moduleInstance = {};
    var ModuleCacheService = {
      getModule: getModule,
      saveModuleLocally: saveModuleLocally
    };

    return ModuleCacheService;

    function getModule() {
      return moduleInstance;
    }

    function saveModuleLocally(module) {
      moduleInstance = module;
    }

  }
})();