(function(){
    'use strict';

    angular
    .module('crowdsource.directives', [])
    .directive('backendError', backendError)
    .directive('compareTo', compareTo)
    .directive('hoverClass', hoverClass)
    ;

    /**
     * @name backendError
     * @desc Clear backend error if input value has been modified.
     *       This helps in ensuring field is re-validated from backend
     */
    function backendError() {
        return {
            restrict: 'A',
            require: '?ngModel',
            link: function (scope, element, attrs, ctrl) {
                return element.on('change', function () {
                    return scope.$apply(function () {
                        return ctrl.$setValidity('backend', true);
                    });
                });
            }
        };
    }

    /**
     * @name compareTo
     * @desc Show error if two values are not same
     */
    function compareTo() {
        return {
            require: "ngModel",
            restrict: 'A',
            scope: {
                compareTo: '='
            },
            link: function(scope, elem, attrs, ctrl) {
                if(!ctrl) {
                    console && console.warn('Match validation requires ngModel to be on the element');
                    return;
                }

                scope.$watch(function() {
                    var modelValue = angular.isUndefined(ctrl.$modelValue)? ctrl.$$invalidModelValue : ctrl.$modelValue;
                    return (ctrl.$pristine && angular.isUndefined(modelValue)) || scope.compareTo === modelValue;
                }, function(currentValue) {
                    ctrl.$setValidity('compareTo', currentValue);
                });
            }
        };
    }

    function hoverClass() {
        return {
            restrict: 'A',
            scope: {
                hoverClass: '@'
            },
            link: function (scope, element) {
                element.on('mouseenter', function () {
                    element.addClass(scope.hoverClass);
                });
                element.on('mouseleave', function () {
                    element.removeClass(scope.hoverClass);
                });
            }
        }
    }
})();