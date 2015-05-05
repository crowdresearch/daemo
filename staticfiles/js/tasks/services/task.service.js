/**
 * Created by milad on 5/5/15.
 */
/**
 * Created by milad on 5/5/15.
 */


/**
* Task
* @namespace crowdsource.task.services
*/
(function () {
  'use strict';

  angular
    .module('crowdsource.task.services')
    .factory('Task', Task);

  Task.$inject = [ '$http'];



  function Task( $http) {
    /**
    * @name TaskSearch
    * @desc The Factory to be returned
    */
    var Task = {
      getTasks : getTasks
    };

    return Task;

    ////////////////////

      function getTasks()
      {
          return $http.get("/api/module/?format=json");
      }
  }


})();