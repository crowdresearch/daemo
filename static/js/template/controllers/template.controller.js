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
        self.select = select;
        self.deselect = deselect;
        self.copy = copy;
        self.removeItem = removeItem;
        self.addComponent = addComponent;
        self.showTaskDesign = showTaskDesign;

        self.items_with_data = [];

        self.userAccount = Authentication.getAuthenticatedAccount();

        if (!self.userAccount) {
            $location.path('/login');
            return;
        }

        var idGenIndex = 0;

        // Retrieve from service if possible.
        //$scope.project.currentProject = Project.retrieve();

        /*if ($scope.project.currentProject.template) {
         self.templateName = $scope.project.currentProject.template.name || generateRandomTemplateName();
         self.items = $scope.project.currentProject.template.items || [];
         } else {
         self.templateName = generateRandomTemplateName();
         self.items = [];
         }*/

        self.items = _.map(self.items, function (item) {
            if (item.hasOwnProperty('isSelected')) {
                delete item.isSelected;
            }
            return item;
        });

        self.selectedItem = null;

        self.templateComponents = Template.getTemplateComponents($scope);

        function buildHtml(item) {
            var html = Template.buildHtml(item);
            return $sce.trustAsHtml(html);
        }

        function deselect(item) {
            if (self.selectedItem && self.selectedItem.hasOwnProperty('isSelected') && self.selectedItem === item) {
                self.selectedItem.isSelected = false;
                self.selectedItem = null;
            }
        }

        function select(item) {

            // deselect earlier item and select this one
            if (self.selectedItem && self.selectedItem.hasOwnProperty('isSelected')) {
                self.selectedItem.isSelected = false;
            }

            self.selectedItem = item;
            item.isSelected = true;
        }

        function copy(item) {
            deselect(item);
            var component = _.find(self.templateComponents, function (component) {
                return component.type == item.type
            });

            var field = angular.copy(component);
            var curId = generateId();

            delete field['description'];
            field.id_string = 'item' + curId;
            field.name = 'item' + curId;
            field.label = item.label;
            field.values = item.values;

            addComponent(field);
        }

        function removeItem(item) {
            var index = self.items.indexOf(item);
            Template.deleteItem(item.id).then(
                function success(response) {

                },
                function error(response) {
                    $mdToast.showSimple('Could not delete template item.');
                }
            ).finally(function () {
            });
            self.items.splice(index, 1);
            self.selectedItem = null;

        }

        $scope.$watch('project.module', function (newValue, oldValue) {
            if (!angular.equals(newValue, oldValue) && newValue.hasOwnProperty('template') && self.items.length == 0) {
                self.items = newValue.template[0].template_items;
            }
        }, true);
        function addComponent(component) {

            if (self.selectedItem && self.selectedItem.hasOwnProperty('isSelected')) {
                self.selectedItem.isSelected = false;
            }

            var field = angular.copy(component);
            var curId = generateId();

            delete field['description'];

            field.id_string = 'item' + curId;
            field.name = 'item' + curId;

            angular.extend(field, {template: $scope.project.module.template[0].id});
            angular.extend(field, {position: self.items.length + 1});

            Template.addItem(field).then(
                function success(response) {
                    angular.extend(field, {id: response[0].id});
                    self.items.push(field);
                },
                function error(response) {
                    $mdToast.showSimple('Could not update project name.');
                }
            ).finally(function () {
            });

            //sync();
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
            $scope.project.template = {
                name: self.templateName,
                items: self.items
            }
        }

        //Show Modal Pop-up of the Task Design Output
        function showTaskDesign(previewButton) {
            update_item_data();

            $mdDialog.show({
                template: '<md-dialog class="centered-dialog" aria-label="preview">' +
                '<md-dialog-content md-scroll-y>' +
                '<div layout-margin>' +
                '<h3><span ng-bind="project.name"></span></h3>' +
                '<p ng-bind="project.description"></p>' +
                '<md-divider></md-divider>' +
                '<p ng-bind="project.taskDescription"></p>' +
                '</div>' +
                '<md-list class="no-decoration-list">' +
                '   <md-list-item class="template-item" ng-repeat="item in template.items_with_data">' +
                '       <div layout="row" flex="100">' +
                '           <div flex="85" style="outline:none">' +
                '               <div md-template-compiler="item" style="cursor: default" editor="false"></div>' +
                '           </div>' +
                '       </div>' +
                '   </md-list-item>' +
                '</md-list>' +
                '</md-dialog-content>' +
                '</md-dialog>',
                parent: angular.element(document.body),
                scope: $scope,
                targetEvent: previewButton,
                preserveScope: true,
                clickOutsideToClose: true
            });
        }

        function replaceAll(find, replace, str) {
            return str.replace(new RegExp(find, 'g'), replace);
        }

        function update_item_data() {
            angular.copy(self.items, self.items_with_data);
            self.items_with_data = _.map(self.items_with_data, function (obj) {

                if ($scope.project.milestone.metadata && $scope.project.milestone.metadata.hasOwnProperty("column_headers")) {
                    angular.forEach($scope.project.milestone.metadata.column_headers, function (header) {
                        var search = header.slice(1, header.length - 1);

                        obj.label = replaceAll(header, $scope.project.milestone.metadata.first[search], obj.label);
                        obj.values = replaceAll(header, $scope.project.milestone.metadata.first[search], obj.values);
                    });
                }

                // this will trigger recompiling of template
                delete obj.isSelected;

                return obj;
            });
        }

        $scope.$on("$destroy", function () {
            sync();
            //Project.syncLocally($scope.project.currentProject);
        });
    }

})();
