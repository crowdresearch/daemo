/**
 * Created by dmorina on 27/06/15.
 */

/**
 * mdTemplateCompilerDirective
 * @namespace crowdsource.template.directives
 */
(function () {
    'use strict';
    angular
        .module('crowdsource.message.directives')
        .directive('mdEnter', mdEnter);

    function mdEnter() {
        return function ($scope, element, attrs) {
            element.bind("keydown keypress", function (event) {
                if (event.which === 13) {
                    $scope.$apply(function () {
                        $scope.$eval(attrs.mdEnter, {'event': event});
                    });
                    event.preventDefault();
                }
            });
        };
    }
})();
