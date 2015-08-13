/**
 * labeled input directive
 * @namespace crowdsource.template.directives
 */
(function () {
    angular
        .module('crowdsource.template.directives')
        .directive('labeled-input', ['$sce', function($sce) {
            return {
                restrict: 'E',
                require: '?ngModel',
                link: function(scope, elements, attrs, ngModel) {
                    if(!ngModel) return;
                    
                }

            }

        }
    function mdTemplateCompilerDirective($parse, $sce, $compile){
        return {
            restrict: 'A',
            link: function(scope, element, attrs){
                var item =  $sce.parseAsHtml(attrs.mdTemplateCompiler);

                var getItem = function () {
                    return item(scope);
                };
                scope.$watch(getItem, function (newValue) {
                    var template = angular.element(newValue);
                    var linkFn = $compile(template);
                    var el = linkFn(scope);
                    if (element.children().length){
                        $(element.children()[0]).replaceWith(el);
                    }
                    else {
                        element.append(el);
                    }
                });

            }
        };
    }
})();