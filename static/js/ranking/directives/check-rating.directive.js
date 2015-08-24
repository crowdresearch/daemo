/**
 * Created by dmorina on 07/05/15.
 */
/**
* Check rating directive
* @namespace crowdsource.data-table.controllers
*/
(function () {
    'use strict';

    angular
      .module('crowdsource.ranking.directives')
      .directive('checkRating', checkRatingDirective);

    function checkRatingDirective(){
        return {
            restrict: 'EA',
            transclude: false,
            scope: false,
            link: function(scope, element, attrs){

            }
        };
    }
})();