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
                editor: '=',
                instance: '='
            },
            link: function (scope, element, attrs, ctrl) {
                scope.item = scope.mdTemplateCompiler;
                var templateNames = {
                    "text": scope.editor ? "text-edit" : "text",
                    "number": scope.editor ? "text-edit" : "text",
                    "text_area": scope.editor ? "text-edit" : "text",
                    "checkbox": scope.editor ? "select-edit" : "select",
                    "select_list": scope.editor ? "select-edit" : "select",
                    "radio": scope.editor ? "select-edit" : "select",
                    "image": scope.editor ? "media-edit" : "media",
                    "audio": scope.editor ? "media-edit" : "media",
                    "video": scope.editor ? "media-edit" : "media"
                };
                var templateComponents = Template.getTemplateComponents(scope);

                function update(newField, oldField) {
                    var type = newField.sub_type || newField.type;
                    Template.getTemplate(templateNames[type]).then(function (template) {
                        var el = angular.element(template);
                        element.html(el);
                        $compile(el)(scope);
                    });

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
                var timeouts = {};
                if (scope.editor) {
                    scope.$watch('item', function (newValue, oldValue) {
                        if (!angular.equals(newValue, oldValue)) {
                            var component = _.find(templateComponents, function (component) {
                                return component.type == newValue.type
                            });
                            var request_data = {};
                            angular.forEach(component.watch_fields, function (obj) {
                                if (newValue[obj] != oldValue[obj]) {
                                    request_data[obj] = newValue[obj];
                                }
                            });
                            if (angular.equals(request_data, {})) return;
                            if (timeouts[newValue.id]) $timeout.cancel(timeouts[newValue.id]);
                            timeouts[newValue.id] = $timeout(function () {
                                Template.updateItem(newValue.id, request_data).then(
                                    function success(response) {

                                    },
                                    function error(response) {
                                        //$mdToast.showSimple('Could not delete template item.');
                                    }
                                ).finally(function () {
                                });
                            }, 2048);
                        }
                    }, true);
                }


            }
        };
    }
})();
