/**
 * Project
 * @namespace crowdsource.template.services
 */
(function () {
    'use strict';

    angular
        .module('crowdsource.template.services')
        .factory('Template', Template);

    Template.$inject = ['$cookies', '$http', '$q', '$sce', 'HttpService', '$templateCache'];

    /**
     * @namespace Template
     * @returns {Factory}
     */

    function Template($cookies, $http, $q, $sce, HttpService, $templateCache) {
        /**
         * @name Template
         * @desc The Factory to be returned
         */
        var Template = {
            getCategories: getCategories,
            getTemplateComponents: getTemplateComponents,
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

            var templateComponents = [
                {
                    name: "Text",
                    icon: 'text_fields',
                    type: 'text',
                    sub_type: 'text',
                    tooltip: "Text",
                    role: 'input',
                    watch_fields: ['aux_attributes', 'type', 'sub_type'],
                    aux_attributes: {
                        question: {
                            value: "Untitled Question",
                            data_source: null
                        },
                        pattern: null,
                        max_length: null,
                        min_length: null,
                        placeholder: 'text field'
                    },
                    position: null,
                    required: true

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
                            value: "Untitled Question",
                            data_source: null
                        },
                        layout: 'column',
                        options: [
                            {
                                value: 'Option 1',
                                data_source: null,
                                position: 1
                            },
                            {
                                value: 'Option 2',
                                data_source: null,
                                position: 2
                            }
                        ],
                        shuffle_options: false
                    },
                    position: null,
                    required: true
                },
                {

                    name: "Radio Button",
                    icon: 'radio_button_checked',
                    type: 'radio',
                    tooltip: "Radio Button",
                    layout: 'column',
                    role: 'input',
                    data_source: null,
                    watch_fields: ['aux_attributes', 'type'],
                    aux_attributes: {
                        question: {
                            value: "Untitled Question",
                            data_source: null
                        },
                        layout: 'column',
                        options: [
                            {
                                value: 'Option 1',
                                data_source: null,
                                position: 1
                            },
                            {
                                value: 'Option 2',
                                data_source: null,
                                position: 2
                            }
                        ],
                        shuffle_options: false
                    },
                    position: null,
                    required: true
                },
                {
                    name: "Select List",
                    icon: 'list',
                    type: 'select_list',
                    tooltip: "Select List",
                    layout: 'column',
                    role: 'input',
                    data_source: null,
                    watch_fields: ['aux_attributes', 'type'],
                    aux_attributes: {
                        question: {
                            value: "Untitled Question",
                            data_source: null
                        },
                        layout: 'column',
                        options: [
                            {
                                value: 'Option 1',
                                data_source: null,
                                position: 1
                            },
                            {
                                value: 'Option 2',
                                data_source: null,
                                position: 2
                            }
                        ],
                        shuffle_options: false
                    },
                    position: null,
                    required: true
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
                            value: "Untitled Question",
                            data_source: null
                        },
                        src: 'http://placehold.it/600x150?text=Image',
                        data_source: null
                    },
                    position: null,
                    required: true
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
                            value: "Untitled Question",
                            data_source: null
                        },
                        src: 'http://www.noiseaddicts.com/samples_1w72b820/3724.mp3',
                        data_source: null
                    },
                    position: null,
                    required: true
                },
                /*{
                 tooltip: "Video Container",
                 layout: 'column',
                 data_source: null,
                 role: 'display',
                 label: '',
                 name: "Video Container",
                 icon: 'play_circle_outline',
                 type: 'video'
                 },*/
                {
                    name: "Remote Content",
                    icon: 'code',
                    type: 'iframe',
                    tooltip: "Embed content from remote site",
                    role: 'display',
                    watch_fields: ['aux_attributes'],
                    position: null,
                    required: true,
                    aux_attributes: {
                        question: {
                            value: "Untitled Form",
                            data_source: null
                        },
                        src: 'http://www.noiseaddicts.com/',
                        data_source: null
                    }
                }
            ];

            return templateComponents;
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
