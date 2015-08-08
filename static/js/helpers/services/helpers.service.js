/*
  Query Filter Services
 */

(function () {
  "use strict";

  angular
    .module('crowdsource.helper.services')
    .factory('queryFilter', queryFilter);

  function queryFilter() {
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

