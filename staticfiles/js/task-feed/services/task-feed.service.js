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
    var selectedCategories = [];
    var TaskFeed = {
      addProject: addProject,
      toggle: toggle,
      selectedCategories: selectedCategories,
      getCategories: getCategories
    };

    return TaskFeed;


    /**
    * @name addProject
    * @desc Try to create a new project
    * @returns {Promise}
    * @memberOf crowdsource.project.services.TaskFeed
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

    function getCategories(){
      return $http({
        url: '/api/category/',
        method: 'GET'
      });
    }
  }
})();