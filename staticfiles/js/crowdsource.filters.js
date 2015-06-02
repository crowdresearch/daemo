/**
 * Filters
 * Author: Shirish Goyal
 */
(function(){
    'use strict';

    angular
    .module('crowdsource.filters', [])
    .filter('concatBy', concatBy);

    function concatBy() {
        return function (input, delimiter) {
            return (input || []).join(delimiter || ', ');
        };
    }

})();