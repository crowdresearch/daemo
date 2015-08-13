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
        .module('crowdsource.template.directives')
        .directive('mdTemplateCompiler', mdTemplateCompilerDirective);

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