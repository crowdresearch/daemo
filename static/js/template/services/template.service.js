/**
 * Project
 * @namespace crowdsource.template.services
 */
(function () {
    'use strict';

    angular
        .module('crowdsource.template.services')
        .factory('Template', Template);

    Template.$inject = ['$cookies', '$http', '$q', '$location', '$sce', 'HttpService', '$templateCache'];

    /**
     * @namespace Template
     * @returns {Factory}
     */

    function Template($cookies, $http, $q, $location, $sce, HttpService, $templateCache) {
        /**
         * @name Template
         * @desc The Factory to be returned
         */
        var Template = {
            getCategories: getCategories,
            getTemplateComponents: getTemplateComponents,
            buildHtml: buildHtml,
            addItem: addItem,
            updateItem: updateItem,
            deleteItem: deleteItem,
            getTemplate: getTemplate
        };

        return Template;

        function getCategories() {
            return $http({
                url: '/api/category/',
                method: 'GET'
            });
        }

        var asyncTemplateCalls = {};

        function getTemplate(item_type) {
            var def = $q.defer();
            var template = '';
            template = $templateCache.get(item_type+".html");
            if (typeof template === "undefined") {
                $http.get("/static/templates/template/components/"+item_type+".html")
                    .success(function (data) {
                        $templateCache.put(item_type+".html", data);
                        def.resolve(data);
                    });
            } else {
                def.resolve(template);
            }
            return def.promise;
        }

        function getTemplateComponents(scope) {
            var itemToolbar = '<div class="template-item-toolbar" layout-align="end start">' +
                '<md-button class="pointer-cursor" ' +
                'ng-click="instance.copy(item)" layout="row" flex> ' +
                '<md-icon md-font-set="material-icons">content_copy</md-icon> ' +
                '</md-button> ' +
                '<md-button class="pointer-cursor" ' +
                'ng-click="instance.removeItem(item)" layout="row" layout-align="center start" ' +
                'flex>' +
                '<md-icon md-font-set="material-icons">delete</md-icon>' +
                '</md-button>' +
                '</div>';

            var templateComponents = [
                {
                    name: "Text",
                    icon: 'text_fields',
                    type: 'text',
                    sub_type: 'text',
                    tooltip: "Text",
                    watch_fields: ['aux_attributes', 'type', 'sub_type'],
                    aux_attributes: {
                        question: {
                            source: "static",
                            value: "Untitled Question",
                            description: null
                        },
                        pattern: null,
                        max_length: null,
                        min_length: null,
                        placeholder: 'text field'
                    },
                    position: null,
                    required: true,
                    toHTML: function () {

                    },
                    toEditor: function () {

                    }
                },
                {
                    name: "Checkbox",
                    icon: 'check_box',
                    type: 'checkbox',
                    tooltip: "Check Box",
                    role: 'input',
                    watch_fields: ['aux_attributes', 'type'],
                    aux_attributes: {
                        question: {
                            source: "static",
                            value: "Untitled Question",
                            description: null
                        },
                        layout: 'column',
                        options: [
                            {
                                source: 'static',
                                value: 'Option 1',
                                position: 1
                            },
                            {
                                source: 'static',
                                value: 'Option 2',
                                position: 2
                            }
                        ],
                        shuffle_options: false
                    },
                    position: null,
                    required: true,
                    toHTML: function () {

                    },
                    toEditor: function () {

                    }
                },
                {

                    name: "Radio Button",
                    icon: 'radio_button_checked',
                    type: 'radio',
                    tooltip: "Radio Button",
                    layout: 'column',
                    data_source: null,
                    watch_fields: ['aux_attributes', 'type'],
                    aux_attributes: {
                        question: {
                            source: "static",
                            value: "Untitled Question",
                            description: null
                        },
                        layout: 'column',
                        options: [
                            {
                                source: 'static',
                                value: 'Option 1',
                                position: 1
                            },
                            {
                                source: 'static',
                                value: 'Option 2',
                                position: 2
                            }
                        ],
                        shuffle_options: false
                    },
                    position: null,
                    required: true,
                    toHTML: function () {

                    },
                    toEditor: function () {

                    }
                },
                {
                    name: "Select List",
                    icon: 'list',
                    type: 'select_list',
                    tooltip: "Select List",
                    layout: 'column',
                    data_source: null,
                    watch_fields: ['aux_attributes', 'type'],
                    aux_attributes: {
                        question: {
                            source: "static",
                            value: "Untitled Question",
                            description: null
                        },
                        layout: 'column',
                        options: [
                            {
                                source: 'static',
                                value: 'Option 1',
                                position: 1
                            },
                            {
                                source: 'static',
                                value: 'Option 2',
                                position: 2
                            }
                        ],
                        shuffle_options: false
                    },
                    position: null,
                    required: true,
                    toHTML: function () {

                    },
                    toEditor: function () {

                    }
                },
                {
                    name: "Image",
                    icon: 'photo',
                    type: 'image',
                    tooltip: "Image Container",
                    role: 'display',
                    watch_fields: ['type', 'aux_attributes'],
                    aux_attributes: {
                        question: {
                            source: "static",
                            value: "Untitled Question",
                            description: null
                        },
                        src: 'http://placehold.it/600x150?text=Image'
                    },
                    position: null,
                    required: true,
                    toHTML: function () {

                    },
                    toEditor: function () {

                    }
                },
                {
                    name: "Audio",
                    icon: 'music_note',
                    type: 'audio',
                    tooltip: "Audio Container",
                    role: 'display',
                    watch_fields: ['type', 'aux_attributes'],
                    aux_attributes: {
                        question: {
                            source: "static",
                            value: "Untitled Question",
                            description: null
                        },
                        src: 'http://www.noiseaddicts.com/samples_1w72b820/3724.mp3'
                    },
                    position: null,
                    required: true,
                    toHTML: function () {

                    },
                    toEditor: function () {

                    }
                }
                /*{
                 tooltip: "Video Container",
                 layout: 'column',
                 data_source: null,
                 role: 'display',
                 label: '',
                 name: "Video Container",
                 icon: 'play_circle_outline',
                 type: 'video'
                 },
                 {
                 tooltip: "External Content (iFrame)",
                 layout: 'column',
                 data_source: null,
                 role: 'display',
                 label: '',
                 name: "iFrame",
                 icon: 'web',
                 type: 'video'
                 }*/
            ];

            return templateComponents;
        }

        function buildHtml(item) {
            var html = '';
            if (item.type === 'label') {
                html = '<' + item.sub_type + ' style="word-wrap:break-word">' + item.values + '</' + item.sub_type + '>';
            }
            else if (item.type === 'image') {
                html = '<img class="image-container" src="' + item.values + '">' + '</img>';
            }
            else if (item.type === 'radio') {
                html = '<md-radio-group class="template-item" ng-model="item.answer" layout="' + item.layout + '">' +
                    '<md-radio-button tabindex="' + item.tabIndex + '" ng-repeat="option in item.values.split(\',\')" value="{{option}}">{{option}}</md-radio-button>';
            }
            else if (item.type === 'checkbox') {
                html = '<div  layout="' + item.layout + '" layout-wrap><div class="template-item" ng-repeat="option in item.values.split(\',\')" >' +
                    '<md-checkbox tabindex="' + item.tabIndex + '"> {{ option }}</md-checkbox></div></div> ';
            } else if (item.type === 'text_area') {
                html = '<md-input-container><label>' + item.values + '</label><textarea class="template-item" ng-model="item.answer" layout="' +
                    item.layout + '"' + ' tabindex="' + item.tabIndex + '"></textarea></md-input-container>';
            } else if (item.type === 'text_field') {
                html = '<md-input-container><label>' + item.values + '</label><input type="text" class="template-item" ng-model="item.answer" layout="' +
                    item.layout + '"' + ' tabindex="' + item.tabIndex + '"/></md-input-container>';
            } else if (item.type === 'select') {
                html = '<md-select class="template-item" ng-model="item.answer" layout="' + item.layout + '">' +
                    '<md-option tabindex="' + item.tabIndex + '" ng-repeat="option in item.values.split(\',\')" value="{{option}}">{{option}}</md-option></md-select>';
            } else if (item.type === 'labeled_input') {
                html = '<div layout="row" style="word-wrap:break-word"><' + item.sub_type + ' flex="75" layout="column">' + item.values + '</' +
                    item.sub_type + '><md-input-container flex="25" layout="column">' +
                    '<label>Enter text here</label>' +
                    '<input tabindex="' + item.tabIndex + '" type="text" class="ranking-item" ng-model="item.answer">' +
                    '</md-input-container></div>';
            }
            else if (item.type === 'audio') {
                html = '<audio src="' + item.values + '" controls> <p>Your browser does not support the <code>audio</code> element.</p> </audio>';
            }
            return html;
        }

        function addItem(data) {
            var settings = {
                url: '/api/template-item/',
                method: 'POST',
                data: data
            };
            return HttpService.doRequest(settings);
        }

        function updateItem(pk, data) {
            var settings = {
                url: '/api/template-item/' + pk + '/',
                method: 'PUT',
                data: data
            };
            return HttpService.doRequest(settings);
        }

        function deleteItem(pk) {
            var settings = {
                url: '/api/template-item/' + pk + '/',
                method: 'DELETE'
            };
            return HttpService.doRequest(settings);
        }
    }
})();
