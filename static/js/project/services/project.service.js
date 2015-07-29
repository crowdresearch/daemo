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
    var instance = {
      totalTasks: 1
    };
    var Project = {
      syncLocally: syncLocally,
      retrieve: retrieve,
      addProject: addProject,
      getCategories: getCategories,
      getReferenceData: getReferenceData,
      getProjects: getProjects,
      clean: clean,
      addDriveFolder: addDriveFolder,
      getFiles: getFiles
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
          description: project.description,
          categories: project.categories,
          csvData: project.uploadedCSVData
        }
      };
      return HttpService.doRequest(settings);
    }

    function getProjects() {
      var settings = {
        url: '/api/project/',
        method: 'GET'
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

    function clean() {
      instance = {};
    }

    function addDriveFolder(name, parent) {
      var settings = {
        url: '/api/google-drive/add-folder/',
        data: {
          name: name,
          parent: parent
        },
        method: 'POST'
      };
      return HttpService.doRequest(settings);
    }

    function getFiles(parent) {
      var settings = {
        url: '/api/google-drive/get-files/',
        data: {
          parent: parent
        },
        method: 'POST'
      };
      return HttpService.doRequest(settings);
    }


  }
})();
