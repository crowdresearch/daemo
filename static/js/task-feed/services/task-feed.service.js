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
    var TaskFeed = {
      getCategories: getCategories,
      getProjects: getProjects,
      getModules: getModules,
      saveComment: saveComment
    };

    return TaskFeed;

    function getProjects () {
      var settings = {
        url: '/api/project/',
        method: 'GET'
      };
      return HttpService.doRequest(settings);
    }
    function getModules () {
      var settings = {
        url: '/api/module/',
        method: 'GET'
      };
      return HttpService.doRequest(settings);
    }

    function getCategories(){
      var settings = {
        url: '/api/category/',
        method: 'GET'
      };
      return HttpService.doRequest(settings);
    }
     function saveComment(module_id, comment){
      var settings = {
        url: '/api/module/'+module_id+'/post_comment/',
        method: 'POST',
        data: {
            comment: {
                body: comment
            }
        }
      };
      return HttpService.doRequest(settings);
    }
  }
})();