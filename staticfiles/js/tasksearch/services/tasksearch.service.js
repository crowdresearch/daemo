/**
 * Created by milad on 5/5/15.
 */


/**
* Tasksearch
* @namespace crowdsource.tasksearch.services
*/
(function () {
  'use strict';

  angular
    .module('crowdsource.tasksearch.services')
    .factory('TaskSearch', TaskSearch);

  TaskSearch.$inject = [ '$http'];



  function TaskSearch( $http) {
    /**
    * @name TaskSearch
    * @desc The Factory to be returned
    */
    var TaskSearch = {
      getTasks : getTasks
    };

    return TaskSearch;

    ////////////////////

      function getTasks(filter, page)
      {
          return $http.get("/api/module/?format=json");
      }
  }


})();