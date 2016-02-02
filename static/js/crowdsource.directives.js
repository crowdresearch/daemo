(function () {
    'use strict';

    angular
        .module('crowdsource.directives', [])
        .directive('backendError', backendError)
        .directive('compareTo', compareTo)
        .directive('hoverClass', hoverClass)
        .directive('outsideClick', outsideClick);

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
            link: function (scope, elem, attrs, ctrl) {
                if (!ctrl) {
                    console && console.warn('Match validation requires ngModel to be on the element');
                    return;
                }

                scope.$watch(function () {
                    var modelValue = angular.isUndefined(ctrl.$modelValue) ? ctrl.$$invalidModelValue : ctrl.$modelValue;
                    return (ctrl.$pristine && angular.isUndefined(modelValue)) || scope.compareTo === modelValue;
                }, function (currentValue) {
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

    function outsideClick($document) {
        return {
            link: function ($scope, $element, $attributes) {
                var scopeExpression = $attributes.outsideClick,
                    onItemClick = function (event) {
                        var targetX = event.clientX;
                        var targetY = event.clientY;

                        var elementOffsetTop = $element.offset().top - $document.scrollTop();
                        var elementOffsetLeft = $element.offset().left;
                        var elementWidth = $element.width();
                        var elementHeight = $element.height();
                        var targetClass = event.currentTarget.body.className;
                        $scope.item.isSelected = targetX >= elementOffsetLeft && targetX <= elementOffsetLeft + elementWidth && targetY >= elementOffsetTop
                            && targetY <= elementOffsetTop + elementHeight && targetClass.indexOf('md-dialog-is-showing') < 0;
                        $scope.$apply();

                    };
                $document.on("click", onItemClick);

                $element.on('$destroy', function () {
                    $document.off("click", onItemClick);
                });
            }
        };
    }
})();
