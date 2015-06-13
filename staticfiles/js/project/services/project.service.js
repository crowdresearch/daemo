/**
* Project
* @namespace crowdsource.project.services
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
    var Project = {
      addProject: addProject,
      toggle: toggle,
      selectedCategories: selectedCategories,
      getCategories: getCategories
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
        data: {
          name: project.name,
          start_date: project.startDate,
          end_date: project.endDate,
          description: project.description,
          keywords: project.keywords,
          categories: project.categories
        }
      };
      return HttpService.doRequest(settings);
    }            
    function toggle(item) {
          var idx = selectedCategories.indexOf(item);
          if (idx > -1) selectedCategories.splice(idx, 1);
          else selectedCategories.push(item);
    }

    function getCategories(){
      return $http({
        url: '/api/category/',
        method: 'GET'
      });
    }
  }
})();