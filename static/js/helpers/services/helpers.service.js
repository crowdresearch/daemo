/*
  Query Filter Services
 */

(function () {
  "use strict";

  angular
    .module('crowdsource.helpers.services')
    .factory('helpersService', helpersService);

  helpersService.$inject = ['$q'];

  function helpersService($q) {
    return {
      querySearch: querySearch
    }
  }

  function querySearch(obj, query, simulateQuery) {
    var results = query ? obj.filter(createFilterFor(query)) : obj,
        deferred;
    if (simulateQuery) {
      deferred = $q.defer();
      $timeout(function () { deferred.resolve( results ); }, Math.random() * 1000, false);
      return deferred.promise;
    } else {
      return results;
    }
  }

  function createFilterFor(query) {
    return function filterFn(obj) {
      return (obj.indexOf(query) >= 0);
    };
  }
})();

