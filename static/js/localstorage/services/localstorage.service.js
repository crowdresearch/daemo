/**
* LocalStorageService
* @namespace crowdsource.localstorage.services
*/
(function () {
  'use strict';

  angular
    .module('crowdsource.localstorage.services')
    .service('LocalStorage', LocalStorage);

  LocalStorage.$inject = ['$window'];

  /**
  * @namespace LocalStorage
  * @returns {Service}
  */

  function LocalStorage($window) {
    /**
    * @name LocalStorageService
    * @desc The Service to be returned
    */

    var prefix = 'daemo_';

    var LocalStorage = {
      get: get,
      set: set,
      remove: remove
    };

    return LocalStorage;

    function get(key, defaultValue) {
      var value = $window.localStorage.getItem(prefix+key, null);

      if(value==null && defaultValue){
          $window.localStorage.setItem(prefix+key, JSON.stringify(defaultValue));
      }

      return JSON.parse($window.localStorage.getItem(prefix+key));
    }

    function set(key, value) {
      $window.localStorage.setItem(prefix+key, JSON.stringify(value));
    }

    function remove(key) {
      return $window.localStorage.removeItem(prefix+key);
    }
  }
})();