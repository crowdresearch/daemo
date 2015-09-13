/**
 * TaskFeedController
 * @namespace crowdsource.template.controllers
 * @author dmorina
 */
(function () {
    'use strict';

    angular
        .module('crowdsource.template.controllers')
        .controller('TemplateController', TemplateController);

    TemplateController.$inject = ['$window', '$location', '$scope', 'Template', '$filter', '$sce',
        'Project', 'Authentication', '$mdDialog'];

    /**
     * @namespace TemplateController
     */
    function TemplateController($window, $location, $scope, Template, $filter, $sce, Project, Authentication, $mdDialog) {
        var self = this;

        self.buildHtml = buildHtml;
        self.setSelectedItem = setSelectedItem;
        self.removeItem = removeItem;
        $scope.onOver = onOver;
        $scope.onDrop = onDrop;
        self.showTaskDesign = showTaskDesign;

        self.items_with_data = [];

        self.userAccount = Authentication.getAuthenticatedAccount();

        if (!self.userAccount) {
            $location.path('/login');
            return;
        }

        var idGenIndex = 0;

        // Retrieve from service if possible.
        $scope.project.currentProject = Project.retrieve();

        if ($scope.project.currentProject.template) {
            self.templateName = $scope.project.currentProject.template.name || generateRandomTemplateName();
            self.items = $scope.project.currentProject.template.items || [];
        } else {
            self.templateName = generateRandomTemplateName();
            self.items = [];
        }

        self.selectedTab = 0;
        self.selectedItem = null;


        self.templateComponents = [
            {
                name: "Label",
                icon: 'format_size',
                type: 'label',
                description: "Use for static text: labels, headings, paragraphs",
                layout: 'column',
                data_source: null,
                role: 'display',
                sub_type: 'h4',
                values: 'Label'
            },
            {
                name: "Checkbox",
                icon: 'check_box',
                type: 'checkbox',
                description: "Use for selecting multiple options",
                layout: 'column',
                data_source: null,
                role: 'input',
                sub_type: 'div',
                values: 'Option 1, Option 2, Option 3'
            },
            {

                name: "Radio Button",
                icon: 'radio_button_checked',
                type: 'radio',
                description: "Use when only one option needs to be selected",
                layout: 'column',
                data_source: null,
                role: 'input',
                sub_type: 'div',
                values: 'Option 1, Option 2, Option 3'
            },
            {

                name: "Select List",
                icon: 'list',
                type: 'select',
                description: "Use for selecting multiple options from a larger set",
                layout: 'column',
                data_source: null,
                role: 'input',
                sub_type: 'div',
                values: 'Option 1, Option 2, Option 3'
            },
            {

                name: "Text Input",
                icon: 'text_format',
                type: 'text_field',
                description: "Use for short text input",
                layout: 'column',
                data_source: null,
                role: 'input',
                sub_type: 'div',
                values: 'Enter text here'
            },
            {

                name: "Text Area",
                icon: 'subject',
                type: 'text_area',
                description: "Use for longer text input",
                layout: 'column',
                data_source: null,
                role: 'input',
                sub_type: 'div',
                values: 'Enter text here'
            },
            {
                name: "Image",
                icon: 'photo',
                type: 'image',
                description: "A placeholder for the image",
                layout: 'column',
                data_source: null,
                role: 'display',
                sub_type: 'div',
                values: 'http://placehold.it/300x300?text=Image'
            },
            {

                name: "Labeled Input",
                icon: 'font_download',
                type: 'labeled_input',
                description: "Use for text fields accompanied by static text",
                layout: 'column',
                data_source: null,
                role: 'input',
                sub_type: 'h4',
                values: 'Label'
            },
            // {
            //   id: 8,
            //   name: "Video Container",
            //   icon: null,
            //   type: 'video',
            //   description: "A placeholder for the video player"
            // },
            {
                name: "Audio",
                icon: 'music_note',
                type: 'audio',
                description: "A placeholder for the audio player",
                layout: 'column',
                data_source: null,
                role: 'display',
                sub_type: 'div',
                values: 'http://www.noiseaddicts.com/samples_1w72b820/3724.mp3'
            }
        ];

        function buildHtml(item) {
            var html = Template.buildHtml(item);
            return $sce.trustAsHtml(html);
        }

        function setSelectedItem(item) {
            self.selectedItem = item;
            self.selectedTab = 1;
        }

        function removeItem(item) {
            var index = self.items.indexOf(item);
            self.items.splice(index, 1);
            self.selectedItem = null;
            self.selectedTab = 0;

            sync();
        }

        function onDrop(event, ui) {
            var draggedItem = ui.draggable.scope();

            if (draggedItem.hasOwnProperty('component')) {
                var field = angular.copy(draggedItem.component);
                var curId = generateId();

                delete field['description'];

                field.id_string = 'item' + curId;
                field.name = 'item' + curId;

                self.items.push(field);
            }

            sync();
        }

        function onOver(event, ui) {
        }

        function generateId() {
            return '' + ++idGenIndex;
        }

        function generateRandomTemplateName() {
            var possible = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
            var random = _.sample(possible, 8).join('');
            return 'template_' + random;
        }

        function sync() {
            $scope.project.currentProject.template = {
                name: self.templateName,
                items: self.items
            }
        }

        //Show Modal Pop-up of the Task Design Output
        function showTaskDesign(previewButton) {
            update_item_data();

            $mdDialog.show({
                template: '<md-dialog class="centered-dialog">' +
                    '<md-dialog-content md-scroll-y>' +
                    '<h3><span ng-bind="project.currentProject.name"></span></h3>' +
                    '<p ng-bind="project.currentProject.description"></p>' +
                    '<md-divider></md-divider>' +
                    '<ul ng-model="template.items" class="no-decoration-list">' +
                    '<li class="template-item" ng-repeat="item in template.items_with_data">' +
                    '<div md-template-compiler="template.buildHtml(item)"></div>' +
                    '</li>' +
                    '</ul>' +
                    '</md-dialog-content>' +
                    '</md-dialog>',
                parent: angular.element(document.body),
                scope: $scope,
                targetEvent: previewButton,
                preserveScope: true,
                clickOutsideToClose: true
            });
        }

        function update_item_data() {
            angular.copy(self.items, self.items_with_data);
            angular.forEach(self.items_with_data, function (obj) {
                if (obj.data_source && $scope.project.currentProject.metadata.first.hasOwnProperty(obj.data_source)) {
                    obj.values = $scope.project.currentProject.metadata.first[obj.data_source];
                }
            });
        }

        $scope.$on("$destroy", function () {
            Project.syncLocally($scope.project.currentProject);
        });
    }

})();