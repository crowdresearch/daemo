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
                instance: '=',
                isDisabled: '=',
                isReview: '=',
                isEditPreview: '=?'
            },
            link: function (scope, element, attrs, ctrl) {
                scope.item = scope.mdTemplateCompiler;

                if (scope.item.aux_attributes.shuffle_options == true && scope.editor == false && scope.isReview == false &&
                    scope.isEditPreview != true) {
                    scope.item.aux_attributes.options = shuffle(scope.item.aux_attributes.options);
                }

                var templateNames = {
                    "instructions": scope.editor ? "instructions-edit" : "instructions",
                    "text": scope.editor ? "text-edit" : "text",
                    "number": scope.editor ? "text-edit" : "text",
                    "text_area": scope.editor ? "text-edit" : "text",
                    "checkbox": scope.editor ? "select-edit" : "select",
                    "select_list": scope.editor ? "select-edit" : "select",
                    "radio": scope.editor ? "select-edit" : "select",
                    "image": scope.editor ? "media-edit" : "media",
                    "audio": scope.editor ? "media-edit" : "media",
                    "video": scope.editor ? "media-edit" : "media",
                    "iframe": scope.editor ? "media-edit" : "media",
                    "file_upload": scope.editor ? "file-upload-edit" : "file-upload"
                };
                var templateComponents = Template.getTemplateComponents(scope);

                function addParam(url, param, value) {
                    var a = document.createElement('a'), regex = /(?:\?|&amp;|&)+([^=]+)(?:=([^&]*))*/gi;
                    var params = {}, match, str = [];
                    a.href = url;
                    while (match = regex.exec(a.search))
                        if (encodeURIComponent(param) != match[1])
                            str.push(match[1] + (match[2] ? "=" + match[2] : ""));
                    str.push(encodeURIComponent(param) + (value ? "=" + encodeURIComponent(value) : ""));
                    a.search = str.join("&");
                    return a.href;
                }

                // Fisher-yates shuffle algorithm
                function shuffle(array) {
                    var m = array.length, t, i;

                    // While there remain elements to shuffle
                    while (m) {
                        // Pick a remaining element…
                        i = Math.floor(Math.random() * m--);

                        // And swap it with the current element.
                        t = array[m];
                        array[m] = array[i];
                        array[i] = t;
                    }

                    return array;
                }

                function update(newField, oldField) {
                    var type = newField.sub_type || newField.type;

                    // For remote content - iframe only
                    if (newField.type == 'iframe' && !scope.editor && newField.hasOwnProperty('identifier') && newField.identifier) {
                        newField.aux_attributes.src = addParam(newField.aux_attributes.src, "daemo_id", newField.identifier);
                        if (newField.hasOwnProperty('daemo_post_url') && newField.daemo_post_url) {
                            newField.aux_attributes.src = addParam(newField.aux_attributes.src, "daemo_post_url",
                                newField.daemo_post_url);
                        }
                    }

                    Template.getTemplate(templateNames[type]).then(function (template) {
                        var el = angular.element(template);
                        element.html(el);
                        $compile(el)(scope);
                    });
                }

                scope.editor = scope.editor || false;
                scope.isDisabled = scope.isDisabled || false;
                scope.isReview = scope.isReview || false;
                scope.isEditPreview = scope.isEditPreview || false;

                scope.bindAutoComplete = function () {
                    var elements = scope.instance.headers;
                    $('.auto-complete-dropdown').textcomplete([
                        {
                            match: /\{\s*([\w\s]*)$/,
                            search: function (term, callback) {
                                var count = 0;
                                callback($.map(elements, function (element) {
                                    if (element.indexOf(term) === 0 && count < 5) {
                                        count++;
                                        return element;
                                    }
                                    else
                                        return null;
                                }));
                            },
                            index: 1,
                            replace: function (element) {
                                return '{{' + element + '}}';
                            }
                        }, {
                            match: /\b([\w\s]*)$/,
                            search: function (term, callback) {
                                var count = 0;
                                callback($.map(elements, function (element) {
                                    if (element.indexOf(term) === 0 && count < 5) {
                                        count++;
                                        return element;
                                    }
                                    else
                                        return null;
                                }));
                            },
                            index: 1,
                            replace: function (element) {
                                return '{{' + element + '}}';
                            }
                        }
                    ]);
                };

                function setUndefinedToNull(obj) {
                    if (obj === undefined) {
                        return null;
                    }
                    if (obj !== null
                        && typeof obj === 'object') {
                        for (var key in obj) {
                            if (obj.hasOwnProperty(key)) {
                                obj[key] = setUndefinedToNull(obj[key]);
                            }
                        }
                    }
                    return obj;
                }

                scope.$watch('mdTemplateCompiler', function (newField, oldField) {

                    if (scope.editor) {
                        // if (!newField.hasOwnProperty('isSelected') || newField.isSelected == undefined || newField.isSelected !== oldField.isSelected) {
                        if (newField !== scope.instance.selectedItem || newField.isNew) {
                            newField.isNew = false;
                            update(newField, oldField);

                        }
                    } else {
                        update(newField, oldField);
                    }

                }, scope.editor);

                var timeouts = {};
                var request_data = {};

                if (scope.editor) {
                    scope.$watch('item', function (newValue, oldValue) {
                        if (!angular.equals(newValue, oldValue)) {
                            if (!request_data.hasOwnProperty(newValue.id)) {
                                request_data[newValue.id] = {};
                            }
                            var component = _.find(templateComponents, function (component) {
                                return component.type == newValue.type
                            });

                            angular.forEach(component.watch_fields, function (property) {
                                if (newValue[property] != oldValue[property]) {
                                    request_data[newValue.id][property] = setUndefinedToNull(newValue[property]);
                                }
                            });
                            if (angular.equals(request_data, {})) return;

                            if (timeouts[newValue.id]) {
                                $timeout.cancel(timeouts[newValue.id]);
                            }
                            if (newValue.id) {
                                scope.$parent.project.saveMessage = 'Saving...';
                            }
                            timeouts[newValue.id] = $timeout(function () {
                                var item = _.find(scope.instance.items, function (item) {
                                    return item.id == newValue.id;
                                });

                                if (item) {
                                    Template.updateItem(newValue.id, request_data[newValue.id]).then(
                                        function success(response) {
                                            scope.$parent.project.saveMessage = 'All changes saved';
                                        },
                                        function error(response) {
                                            //$mdToast.showSimple('Could not delete template item.');
                                        }
                                    ).finally(function () {
                                    });
                                }
                            }, 512);
                        }
                    }, true);
                }


            }
        };
    }
})();
