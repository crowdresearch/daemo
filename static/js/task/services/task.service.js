/**
* TaskService
* @namespace crowdsource.tasks.services
*/
(function () {
  'use strict';

  angular
    .module('crowdsource.task.services')
    .factory('Task', Task);

  Task.$inject = ['$cookies', '$q', '$location', 'HttpService'];

  /**
  * @namespace Task
  * @returns {Factory}
  */

  function Task($cookies, $q, $location, HttpService) {
    /**
    * @name TaskService
    * @desc The Factory to be returned
    */
    var Task = {
      getTaskWithData: getTaskWithData,
      submitTask: submitTask,
      skipTask: skipTask,
      getTasks: getTasks,
      updateStatus: updateStatus,
      downloadResults: downloadResults,
      getTaskComments: getTaskComments,
      saveComment: saveComment
    };

    return Task;

    function getTaskWithData(id, saved){
      if(saved) {
        var settings = {
          url: '/api/task-worker/' + id + '/retrieve_with_data_and_results/',
          method: 'GET',
          params: {
            id: id
          }
        };
      } else {
        var settings = {
          url: '/api/task/' + id + '/retrieve_with_data/',
          method: 'GET'
        };
      }
      return HttpService.doRequest(settings);
    }

    function submitTask(data){
      var settings = {
        url: '/api/task-worker-result/submit-results/',
        method: 'POST',
        data: data
      };
      return HttpService.doRequest(settings);
    }

    function skipTask(task_id){
      var settings = {
        url: '/api/task-worker/'+task_id+'/',
        method: 'DELETE'
      };
      return HttpService.doRequest(settings);
    }

    function getTasks(project_id) {
        var settings = {
          url: '/api/task/list_by_project/',
          method: 'GET',
          params: {
              project_id: project_id
          }
        };

        return HttpService.doRequest(settings);
    }

    function updateStatus(request_data){
        var settings = {
        url: '/api/task-worker/bulk_update_status/',
        method: 'POST',
        data: request_data
      };
      return HttpService.doRequest(settings);
    }

    function downloadResults(params) {
      var settings = {
        url: '/api/csvmanager/download-results/',
        method: 'GET',
        params: params
      };
      return HttpService.doRequest(settings);
    }
    
    function getTaskComments(task_id) {
      var settings = {
        url: '/api/task/'+task_id+'/list_comments/',
        method: 'GET'
      };
      return HttpService.doRequest(settings);
    }

    function saveComment(task_id, comment){
      var settings = {
        url: '/api/task/'+task_id+'/post_comment/',
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