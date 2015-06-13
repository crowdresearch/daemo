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
    var selectedCategories = [];
    var Project = {
      addProject: addProject,
      toggle: toggle,
      selectedCategories: selectedCategories
    };

    return Project;


    /**
    * @name addProject
    * @desc Try to create a new project
    * @returns {Promise}
    * @memberOf crowdsource.project.services.Project
    */
    function addProject(project) {
      return $http({
        url: '/api/project/',
        method: 'POST',
        data: {
          name: project.name,
          start_date: project.startDate,
          end_date: project.endDate,
          description: project.description,
          keywords: project.keywords,
          categories: project.categories
        }
      });
    }            
    function toggle (item) {
          var idx = selectedCategories.indexOf(item);
          if (idx > -1) selectedCategories.splice(idx, 1);
          else selectedCategories.push(item);
    }
  }
})();