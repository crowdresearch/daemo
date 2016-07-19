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
                form: '='
            },
            link: function (scope, element, attrs, ctrl) {
                scope.item = scope.mdTemplateCompiler;

                var validationTypes = {
                    none: {name: "None", value: "none"},
                    email: {name: "Email Address", value: "email"},
                    contains: {name: "Contains", value: "contains"},
                    no_contain: {name: "Doesn't contain", value: "no-contain"},
                    greater: {name: "Greater than", value: "greater"},
                    greater_equal: {name: "Greater than or equal to", value: "greater-equal"},
                    less: {name: "Less than", value: "less"},
                    less_equal: {name: "Less than or equal to", value: "less-equal"},
                    equal: {name: "Equal to", value: "equal"},
                    between: {name: "Between", value: "between"}
                };


                var templateNames = {
                    "instructions": scope.editor ? "instructions-edit" : "instructions",
                    "text": scope.editor ? "text-edit" : "text",
                    "number": scope.editor ? "text-edit" : "text",
                    "text_area": scope.editor ? "text-edit" : "text",
                    "checkbox": scope.editor ? "select-edit" : "select",
                    "select_list": scope.editor ? "select-edit" : "select",
                    "slider": scope.editor ? "slider-edit" : "slider",
                    "radio": scope.editor ? "select-edit" : "select",
                    "image": scope.editor ? "media-edit" : "media",
                    "audio": scope.editor ? "media-edit" : "media",
                    "video": scope.editor ? "media-edit" : "media",
                    "iframe": scope.editor ? "media-edit" : "media"
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

                function update(newField, oldField) {
                    var type = newField.sub_type || newField.type;

                    // For remote content - iframe only
                    if (newField.type == 'iframe' && !scope.editor && newField.hasOwnProperty('identifier') && newField.identifier) {
                        newField.aux_attributes.src = addParam(newField.aux_attributes.src, "daemo_id", newField.identifier);
                    }

                    Template.getTemplate(templateNames[type]).then(function (template) {
                        var el = angular.element(template);
                        element.html(el);
                        $compile(el)(scope);
                    });
                }

                scope.getPatternOptions = function (patternType, type) {
                    if (patternType === 'text') {
                        if (type === 'text') {
                            return [validationTypes.none, validationTypes.contains,
                                validationTypes.no_contain, validationTypes.email];
                        } else if (type === 'text_area') {
                            return [validationTypes.none, validationTypes.contains, validationTypes.no_contain];
                        }
                    } else if (patternType === 'number') {
                        return [validationTypes.none, validationTypes.greater, validationTypes.greater_equal,
                            validationTypes.less, validationTypes.less_equal, validationTypes.equal,
                            validationTypes.between];
                    }
                };

                scope.validateRegex = function (input) {
                    try {
                        var regex = new RegExp(input);
                        scope.isValidRegex = true;
                    } catch(e) {
                        scope.isValidRegex = false;
                    }
                }

                scope.editor = scope.editor || false;

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
                                return '{' + element + '}';
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
                                return '{' + element + '}';
                            }
                        }
                    ]);
                };

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

                            //List of column-values in attached csv.
                            var available_data_sources = scope.instance.headers;

                            //Get the question-text and split it into array of tokens
                            var questionString = request_data['aux_attributes']['question']['value'] || "";
                            var questionStringTokens = questionString.split(/[{\}]{1,2}/);
                            var positionCounter = 0;
                            var dataSources = request_data['aux_attributes']['question']['data_source'] = [];

                            //Iterate through the array of tokens in question-string
                            for (var index in questionStringTokens) {
                                if (questionStringTokens[index]) {
                                    //Check if the current token is 'dynamic' i.e if it matches column-values in attached csv.
                                    if (available_data_sources.indexOf(questionStringTokens[index].replace(/\s+/g, ' ').trim()) > -1) {
                                        var obj = {
                                            type: 'dynamic',
                                            value: questionStringTokens[index],
                                            position: positionCounter
                                        };
                                        request_data['aux_attributes']['question']['data_source'].push(obj);
                                        positionCounter++;
                                    }
                                    else {
                                        if (dataSources[positionCounter] && dataSources[positionCounter].type == 'static') {
                                            request_data['aux_attributes']['question']['data_source'][positionCounter].value += questionStringTokens[index];
                                        }
                                        else {
                                            var obj = {
                                                type: 'static',
                                                value: questionStringTokens[index],
                                                position: positionCounter
                                            };
                                            request_data['aux_attributes']['question']['data_source'].push(obj);
                                            positionCounter++;
                                        }
                                    }
                                }
                            }

                            //Iterate over the available options
                            for (var option in request_data['aux_attributes']['options']) {
                                //Get the option-text and split it into array of tokens
                                var optionString = request_data['aux_attributes']['options'][option]['value'] || "";
                                var optionStringTokens = optionString.split(/[{\}]{1,2}/);
                                positionCounter = 0;
                                dataSources = request_data['aux_attributes']['options'][option]['data_source'] = [];

                                //Iterate through the array of tokens in each option-string
                                for (var index in optionStringTokens) {
                                    if (optionStringTokens[index]) {
                                        //Check if the current token is 'dynamic' i.e if it matches column-values in attached csv.
                                        if (available_data_sources.indexOf(optionStringTokens[index].replace(/\s+/g, ' ').trim()) > -1) {
                                            var obj = {
                                                type: 'dynamic',
                                                value: optionStringTokens[index],
                                                position: positionCounter
                                            };
                                            request_data['aux_attributes']['options'][option]['data_source'].push(obj);
                                            positionCounter++;
                                        }
                                        else {
                                            if (dataSources[positionCounter] && dataSources[positionCounter].type == 'static') {
                                                request_data['aux_attributes']['options'][option]['data_source'][positionCounter].value += optionStringTokens[index];
                                            }
                                            else {
                                                var obj = {
                                                    type: 'static',
                                                    value: optionStringTokens[index],
                                                    position: positionCounter
                                                };
                                                request_data['aux_attributes']['options'][option]['data_source'].push(obj);
                                                positionCounter++;
                                            }
                                        }
                                    }
                                }
                            }

                            if (request_data['aux_attributes']['src']) {
                                //Get the question-text and split it into array of tokens
                                var sourceString = request_data['aux_attributes']['src'] || "";
                                var sourceStringTokens = sourceString.split(/[{\}]{1,2}/);
                                positionCounter = 0;
                                dataSources = request_data['aux_attributes']['data_source'] = [];

                                //Iterate through the array of tokens in question-string
                                for (var index in sourceStringTokens) {
                                    if (sourceStringTokens[index]) {
                                        //Check if the current token is 'dynamic' i.e if it matches column-values in attached csv.
                                        if (available_data_sources.indexOf(sourceStringTokens[index].replace(/\s+/g, ' ').trim()) > -1) {
                                            var obj = {
                                                type: 'dynamic',
                                                value: sourceStringTokens[index],
                                                position: positionCounter
                                            };
                                            request_data['aux_attributes']['data_source'].push(obj);
                                            positionCounter++;
                                        }
                                        else {
                                            if (dataSources[positionCounter] && dataSources[positionCounter].type == 'static') {
                                                request_data['aux_attributes']['data_source'][positionCounter].value += sourceStringTokens[index];
                                            }
                                            else {
                                                var obj = {
                                                    type: 'static',
                                                    value: sourceStringTokens[index],
                                                    position: positionCounter
                                                };
                                                request_data['aux_attributes']['data_source'].push(obj);
                                                positionCounter++;
                                            }
                                        }
                                    }
                                }
                            }

                            if (angular.equals(request_data, {})) return;

                            if (timeouts[newValue.id]) {
                                $timeout.cancel(timeouts[newValue.id]);
                            }

                            timeouts[newValue.id] = $timeout(function () {
                                var item =  _.find(scope.instance.items, function(item){
                                    return item.id == newValue.id;
                                });

                                if(item) {
                                    Template.updateItem(newValue.id, request_data).then(
                                        function success(response) {

                                        },
                                        function error(response) {
                                            //$mdToast.showSimple('Could not delete template item.');
                                        }
                                    ).finally(function () {
                                    });
                                }
                            }, 2048);
                        }
                    }, true);
                }


            }
        };
    }
})();
