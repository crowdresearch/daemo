(function () {
  'use strict';

  angular
    .module('crowdsource.task.services')
    .factory('Task', Task);

  Task.$inject = ['$http'];

  function Task($http) {

    var Task = {
      getList: getList,
      getById: getById,
      getCategories: getCategories,
    };

    return Task;

    function getList(query) {
      return $http({
        url: '/api/module/?format=json',
        method: 'GET',
        data: {
          query: query
        }
      });
    }

    function getCategories () {
      /*
      reutrn $http({
        url: '/api/categories',
        method: 'GET',
      })
      */
      return [
        { id: 1, name: 'Programming', icon: 'fa-file-code-o'},
        { id: 2, name: 'Design',      icon: 'fa-magic'},
        { id: 3, name: 'Movies',      icon: 'fa-film'},
        { id: 4, name: 'Photos',      icon: 'fa-photo'},
        { id: 5, name: 'Accounting',  icon: 'fa-bar-chart'},
        { id: 6, name: 'Legal',       icon: 'fa-legal'},
        { id: 7, name: 'Translation', icon: 'fa-comments-o'},
        { id: 8, name: 'Writing',     icon: 'fa-file-word-o'},
      ]
    }

    function getById(id) {
      return $http({
        url: '/api/module/?format=json',
        method: 'GET',
        data: {
          id: id
        }
      });
    }

  }
})();