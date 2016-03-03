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

    TemplateController.$inject = ['$window', '$state', '$scope', 'Template', '$filter', '$sce', '$mdDialog'];

    /**
     * @namespace TemplateController
     */
    function TemplateController($window, $state, $scope, Template, $filter, $sce, $mdDialog) {
        var self = this;

        self.buildHtml = buildHtml;
        self.select = select;
        self.deselect = deselect;
        self.copy = copy;
        self.removeItem = removeItem;
        self.addComponent = addComponent;
        self.showTaskDesign = showTaskDesign;
        self.getIcon = getIcon;
        self.addOption = addOption;
        self.removeOption = removeOption;
        self.items_with_data = [];
        self.headers = [];
        self.getTrustedUrl = getTrustedUrl;
        self.setDataSource = setDataSource;

        var idGenIndex = 0;

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

            field.name = 'item' + curId;
            field.aux_attributes = item.aux_attributes;

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

        $scope.$watch('project.project', function (newValue, oldValue) {
            if (!angular.equals(newValue, oldValue) && newValue.hasOwnProperty('templates') && self.items.length == 0) {
                self.items = newValue.templates[0].template_items;
            }
            if (!angular.equals(newValue, oldValue) && newValue.hasOwnProperty('batch_files')) {
                if (newValue.batch_files.length==1 && (oldValue.batch_files==undefined ||
                    newValue.batch_files.length != oldValue.batch_files.length)){
                    self.headers = newValue.batch_files[0].column_headers;
                }
                else if (newValue.batch_files.length==1 && newValue.batch_files.length == oldValue.batch_files.length) {

                }
                else {
                    self.headers = [];
                }

            }
        }, true);
        function addComponent(component) {

            if (self.selectedItem && self.selectedItem.hasOwnProperty('isSelected')) {
                self.selectedItem.isSelected = false;
            }

            var field = angular.copy(component);
            var curId = generateId();
            field.name = 'item' + curId;

            angular.extend(field, {template: $scope.project.project.templates[0].id});
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
                '<h3><span ng-bind="project.project.name"></span></h3>' +
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

                if ($scope.project.project.metadata && $scope.project.project.batch_files[0].hasOwnProperty("column_headers")) {
                    angular.forEach($scope.project.project.batch_files[0].column_headers, function (header) {
                        var search = header.slice(1, header.length - 1);

                        obj.label = replaceAll(header, $scope.project.project.batch_files[0].firs_row[search], obj.label);
                        obj.values = replaceAll(header, $scope.project.project.batch_files[0].firs_row[search], obj.values);
                    });
                }

                // this will trigger recompiling of template
                delete obj.isSelected;

                return obj;
            });
        }


        function getIcon(item_type, index){
            if(item_type=='checkbox') return 'check_box_outline_blank';
            else if(item_type=='radio') return 'radio_button_unchecked';
            else if(item_type=='select') return index+'.';
        }
        function addOption(item){
            var option = {
                value: 'Option '+ (item.aux_attributes.options.length + 1)
            };
            item.aux_attributes.options.push(option);
        }
        function removeOption(item, index){
            item.aux_attributes.options.splice(index, 1);
        }
        function getTrustedUrl(url){
            return $sce.trustAsResourceUrl(url);
        }
        function setDataSource(item, data_source){
            if(!item.data_source || item.data_source != data_source){
                item.data_source = data_source;
                if(item.hasOwnProperty('value')) item.value = null;
                if(item.hasOwnProperty('src')) item.src = null;
                item.placeholder = 'will be filled from {' + data_source + '}';
            }
            else {
                item.data_source = null;
                item.placeholder = null;
                if(item.hasOwnProperty('value')) item.value = 'Untitled Question';
                if(item.hasOwnProperty('src')) item.src = null;
            }
        }
    }

})();
