/**
* Project
* @namespace crowdsource.task-feed.services
*/
(function () {
  'use strict';

  angular
    .module('crowdsource.task-feed.services')
    .factory('TaskFeed', TaskFeed);

  TaskFeed.$inject = ['$cookies', '$http', '$q', '$location', 'HttpService'];

  /**
  * @namespace TaskFeed
  * @returns {Factory}
  */

  function TaskFeed($cookies, $http, $q, $location, HttpService) {
    /**
    * @name TaskFeed
    * @desc The Factory to be returned
    */
    var TaskFeed = {
      getCategories: getCategories
    };

    return TaskFeed;

    function getCategories(){
      return $http({
        url: '/api/category/',
        method: 'GET'
      });
    }
  }
})();