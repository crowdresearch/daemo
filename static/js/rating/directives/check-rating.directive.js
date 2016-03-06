/**
 * Check rating directive
 * @namespace crowdsource.rating.directives
 */
(function () {
    'use strict';

    angular
        .module('crowdsource.rating.directives')
        .directive('checkrating', checkrating);

    function checkrating() {
        return {
            restrict: 'EA',
            templateUrl: 'static/templates/rating/checkrating.html',
            scope: {
                clickHandler: "=",
                model: "=",
                selected: "="
            }
        };
    }
})();
