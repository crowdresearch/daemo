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
    * @name register
    * @desc Try to register a new user
    * @param {string} email The email entered by the user
    * @param {string} password The password entered by the user
    * @param {string} username The username entered by the user
    * @returns {Promise}
    * @memberOf crowdsource.authentication.services.Project
    */
    function addProject(email, firstname, lastname, password1, password2) {
      return $http({
        url: '/api/user/',
        method: 'POST',
        data: {
          email: email,
          first_name: firstname,
          last_name: lastname,
          password1: password1,
          password2: password2
        }
      });
    }            

  }
})();