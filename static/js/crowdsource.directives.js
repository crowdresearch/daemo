(function () {
    'use strict';

    angular
        .module('crowdsource.directives', [])
        .directive('backendError', backendError)
        .directive('compareTo', compareTo)
        .directive('hoverClass', hoverClass)
        .directive('outsideClick', outsideClick)
        .directive('isCurrency', isCurrency)
        .directive('autoFocus', autoFocus);

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
                        if($scope.item.isSelected){
                            $element.children()[0].getElementsByClassName('_question')[0]
                                .getElementsByClassName('auto-complete-dropdown')[0].focus();
                        }
                        $scope.$apply();

                    };
                $document.on("click", onItemClick);

                $element.on('$destroy', function () {
                    $document.off("click", onItemClick);
                });
            }
        };
    }

    function autoFocus($timeout) {
        return {
            restrict: 'AC',
            link: function (scope, element) {
                $timeout(function () {
                    element[0].focus();
                }, 0);
            }
        };
    }

    function isCurrency() {
        return {
            require: 'ngModel',
            link: function (scope, element, attrs, ctrl) {
                scope.$watch(attrs.ngModel, function (newValue, oldValue) {
                    var dLen = parseInt(attrs.decimals) + 1;
                    var iLen = parseInt(attrs.integers) + 1;

                    var arr = String(parseFloat(newValue)||0.00).split("");

                    if(arr.length==1 && isNaN(newValue)){
                        // no input
                        ctrl.$setViewValue(0);
                        ctrl.$render();
                    }

                    if (arr.length === 1 && arr[0] === '.') return;

                    if (arr.length === 2 && newValue === '-.') return;

                    var decimalIndex = String(newValue).indexOf('.');

                    if (
                        isNaN(newValue)                                                             // no input
                        || (decimalIndex != -1 && String(newValue).length - decimalIndex > dLen)    // has more than expected decimal values
                        || (decimalIndex == -1 && arr.length === iLen)) {                           // has no decimal point and it is all integers

                        if (scope === undefined || scope == null || newValue == null) {
                            return;
                        }

                        ctrl.$setViewValue(oldValue);
                        ctrl.$render();
                    }
                });
            }
        };
    }

})();
