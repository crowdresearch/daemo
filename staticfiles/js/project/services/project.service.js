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
    var instance = {};
    var Project = {
      syncLocally: syncLocally,
      retrieve: retrieve,
      addProject: addProject,
      getCategories: getCategories,
      getReferenceData: getReferenceData,
      getProjects: getProjects,
      clean: clean
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
          modules: [
            {
              name: 'Prototype Task',
              description: project.milestoneDescription,
              template: [
                {
                  name: project.template.name,
                  share_with_others: true,
                  template_items: project.template.items
                },
              ],
              price: project.payment.wage_per_hit,
              status: 1,
              repetition: project.taskType !== "oneTask",
              number_of_hits: project.payment.number_of_hits,
              module_timeout: 0,
              has_data_set: true,
              data_set_location: ''
            }
          ]
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

  }
})();
