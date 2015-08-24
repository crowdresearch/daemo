/**
* Check rating directive
* @namespace crowdsource.ranking.directives
*/
(function () {
    'use strict';

    angular
      .module('crowdsource.ranking.directives')
      .directive('checkrating', checkrating);

    function checkrating() {
        return {
            restrict: 'EA',
            templateUrl: 'static/templates/ranking/checkrating.html',
            scope: {
                clickHandler: "=",
                model: "=",
                selected:"="
            }
        };
    }
})();