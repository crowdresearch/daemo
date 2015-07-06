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
    var Project = {
      addProject: addProject,
      addPayment: addPayment,
      toggle: toggle,
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
        data: {
          name: project.name,
          description: project.description,
          keywords: project.taskType,
          categories: project.categories
        }
      };
      return HttpService.doRequest(settings);
    }
    function addPayment(payment) {
      var settings = {
        url: 'http://share-quick.com/cr/addPayment.php',
        method: 'POST',
        data: payment
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

    function getReferenceData(){
      return $http({
        url: 'https://api.myjson.com/bins/4ovc8',
        method: 'GET'
      });
    }
  }
})();
