/**
* Project
* @namespace crowdsource.project.services
*/
(function () {
  'use strict';

  angular
    .module('crowdsource.project.services')
    .factory('Project', Project);

  Project.$inject = ['$cookies', '$http', '$q', '$location'];

  /**
  * @namespace Project
  * @returns {Factory}
  */

  function Project($cookies, $http, $q, $location) {
    /**
    * @name Project
    * @desc The Factory to be returned
    */
    var Project = {
      addProject: addProject
    };

    return Project;


    /**
    * @name addProject
    * @desc Try to create a new project
    * @returns {Promise}
    * @memberOf crowdsource.project.services.Project
    */
    function addProject(name, description, details) {
      return $http({
        url: '/api/user/',
        method: 'POST',
        data: {
          name: name,
          description: description,
          details: details
        }
      });
    }            

  }
})();