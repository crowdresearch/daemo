/**
* Project
* @namespace crowdsource.project.services
* @author dmorina neilthemathguy
*/
(function () {
  'use strict';

  angular
    .module('crowdsource.project.services')
    .factory('Project', Project);

  Project.$inject = ['$cookies', '$http', '$q', '$location', 'HttpService'];

  /**
  * @namespace Project
  * @returns {Factory}
  */

  function Project($cookies, $http, $q, $location, HttpService) {
    /**
    * @name Project
    * @desc The Factory to be returned
    */
    var selectedCategories = [];
    var instance = {};
    var Project = {
      syncLocally: syncLocally,
      retrieve: retrieve,
      addProject: addProject,
      selectedCategories: selectedCategories,
      getCategories: getCategories,
      getReferenceData: getReferenceData
    };

    return Project;


    /**
    * @name addProject
    * @desc Try to create a new project
    * @returns {Promise}
    * @memberOf crowdsource.project.services.Project
    */
    function addProject(project) {
      var settings = {
        url: '/api/project/',
        method: 'POST',
        data: project
      };
      return HttpService.doRequest(settings);
    }

    function getCategories() {
      var settings = {
        url: '/api/category/',
        method: 'GET'
      };
      return HttpService.doRequest(settings);
    }

    function getReferenceData() {
      return $http({
        url: 'https://api.myjson.com/bins/4ovc8',
        method: 'GET'
      });
    }

    function syncLocally(projectInstance) {
      instance = projectInstance;
    }

    function retrieve() {
      return instance;
    }
  }
})();
