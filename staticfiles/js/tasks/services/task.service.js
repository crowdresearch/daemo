(function () {
  'use strict';

  angular
    .module('crowdsource.tasks.services')
    .factory('Task', Task);

  Task.$inject = ['$http'];

  function Task($http) {

    var Task = {
      getList: getList,
      getById: getById
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