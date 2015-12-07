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

    function mdTemplateCompilerDirective($parse, $sce, $compile, $timeout, Template) {
        return {
            restrict: 'A',
            replace: true,
            scope: {
                mdTemplateCompiler: '=',
                editor: '='
            },
            link: function (scope, element, attrs, ctrl) {
                scope.item = scope.mdTemplateCompiler;

                var templateComponents = Template.getTemplateComponents(scope);

                function update(newField, oldField) {
                    var format = _.find(templateComponents, function (item) {
                        return item.type == newField.type;
                    });

                    if (newField.hasOwnProperty('isSelected') && newField.isSelected && scope.editor) {
                        newField.toView = format.toEditor;
                    } else {
                        newField.toView = format.toHTML;
                    }

                    // TODO: Make this more robust to handle any CSV format - with quotes, commas
                    if (newField.hasOwnProperty('choices') && _.isString(scope.item.choices)) {
                        var choices = scope.item.choices;

                        scope.item.options = String(choices).split(',').map(function (item) {
                            return item;
                        })
                    }

                    var template = newField.toView();
                    var el = angular.element(template);
                    element.html(el);
                    $compile(el)(scope);
                }

                scope.editor = scope.editor || false;

                scope.$watch('mdTemplateCompiler', function (newField, oldField) {

                    if (scope.editor) {
                        if (!newField.hasOwnProperty('isSelected') || newField.isSelected == undefined || newField.isSelected !== oldField.isSelected) {
                            update(newField, oldField);
                        }
                    } else {
                        update(newField, oldField);
                    }

                }, scope.editor);

            }
        };
    }
})();