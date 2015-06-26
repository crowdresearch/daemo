/**
* Project
* @namespace crowdsource.template.services
*/
(function () {
  'use strict';

  angular
    .module('crowdsource.template.services')
    .factory('Template', Template);

  TaskFeed.$inject = ['$cookies', '$http', '$q', '$location', 'HttpService'];

  /**
  * @namespace Template
  * @returns {Factory}
  */

  function Template($cookies, $http, $q, $location, HttpService) {
    /**
    * @name TaskFeed
    * @desc The Factory to be returned
    */
    var Template = {
      getCategories: getCategories
    };

    return Template;

    function getCategories(){
      return $http({
        url: '/api/category/',
        method: 'GET'
      });
    }
  }
})();