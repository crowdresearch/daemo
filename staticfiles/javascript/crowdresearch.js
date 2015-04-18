/**
 * Created by dmorina on 16/04/15.
 */

(function () {
    'use strict';

    angular
        .module('crowdresearch', [
        'crowdresearch.routes',
        'crowdresearch.user_management'
        ]);

    angular
        .module('crowdresearch.routes', ['ngRoute']);

})();


angular
  .module('crowdresearch')
  .run(run);

run.$inject = ['$http'];

/*matching Django csrf token name*/
function run($http) {
  $http.defaults.xsrfHeaderName = 'X-CSRFToken';
  $http.defaults.xsrfCookieName = 'csrftoken';
}