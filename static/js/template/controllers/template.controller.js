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
  function TemplateController($window, $location, $scope, Template, $filter, $sce,
    Project, Authentication, $mdDialog) {
    var self = this;
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
    self.buildHtml = buildHtml;
    self.setSelectedItem = setSelectedItem;
    self.removeItem = removeItem;
    self.selectedItem = null;
    $scope.onOver = onOver;
    $scope.onDrop = onDrop;
    $scope.sortableOptions = {
      stop: function(e, ui) {
        var newPosition = ui.item.index() + 1;
        var oldPosition = -1;
        for (var i = 0; i < self.items.length; i++) {
          if(self.items[i].id_string === ui.item.scope().item.id_string) {
            oldPosition = self.items[i].position;
            break;
          }
        }
        if(newPosition < oldPosition) {
          for (var i = 0; i < self.items.length; i++) {
            if(self.items[i].position >= newPosition && self.items[i].position < oldPosition) {
              self.items[i].position++;
            }
            if(self.items[i].id_string == ui.item.scope().item.id_string) {
              self.items[i].position = newPosition;
            }
          }
        } else if(newPosition > oldPosition) {
          for(var i = 0; i < self.items.length; i++) {
            if(self.items[i].position <= newPosition && self.items[i].position > oldPosition) {
              self.items[i].position--;
            }
            if(self.items[i].id_string == ui.item.scope().item.id_string) {
              self.items[i].position = newPosition;
            }
          }
        }
      }
    };
    self.templateComponents = [
      {
        id: 1,
        name: "Label",
        icon: null,
        type: 'label',
        description: "Use for static text: labels, headings, paragraphs"
      },
      {
        id: 2,
        name: "Checkbox",
        icon: null,
        type: 'checkbox',
        description: "Use for selecting multiple options"
      },
      {
        id: 3,
        name: "Radio Button",
        icon: null,
        type: 'radio',
        description: "Use when only one option needs to be selected"
      },
      {
        id: 4,
        name: "Select list",
        icon: null,
        type: 'select',
        description: "Use for selecting multiple options from a larger set"
      },
      {
        id: 5,
        name: "Text field",
        icon: null,
        type: 'text_field',
        description: "Use for short text input"
      },
      {
        id: 6,
        name: "Text Area",
        icon: null,
        type: 'text_area',
        description: "Use for longer text input"
      },
      {
        id: 7,
        name: "Image Container",
        icon: null,
        type: 'image',
        description: "A placeholder for the image"
      },
      {
        id: 8,
        name: "Labeled Input",
        icon: null,
        type: 'labeled_input',
        description: "Use for text fields accompanied by static text"
      }
      // {
      //   id: 8,
      //   name: "Video Container",
      //   icon: null,
      //   type: 'video',
      //   description: "A placeholder for the video player"
      // },
      // {
      //   id: 9,
      //   name: "Audio Container",
      //   icon: null,
      //   type: 'audio',
      //   description: "A placeholder for the audio player"
      // }
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
      var oldPosition = -1;
      for (var i = 0; i < self.items.length; i++) {
        if (self.items[i].id_string === item.id_string) {
          oldPosition = self.items[i].position;
          self.items.splice(i, 1);
          break;
        }
      }
      for(var i = 0; i < self.items.length; i++) {
        if(self.items[i].position > oldPosition) {
          self.items[i].position--;
        }
      }
      sync();
    }

    function onDrop(event, ui) {
      var item_type = $(ui.draggable).attr('data-type');
      var curId = generateId();
      if(item_type==='label') {
        var item = {
          id_string: curId,
          name: 'label' + curId,
          type: item_type,
          width: 100,
          height: 100,
          values: 'Label 1',
          role: 'display',
          sub_type: 'h4',
          layout: 'column',
          icon: null,
          data_source: null,
          position: self.items.length + 1
        };
        self.items.push(item);
      }
      else if(item_type==='image') {
        var item = {
          id_string: curId,
          name: 'image_placeholder' + curId,
          type: item_type,
          width: 100,
          height: 100,
          values: null,
          role: 'display',
          sub_type: 'div',
          layout: 'column',
          icon: '/static/bower_components/material-design-icons/image/svg/production/ic_panorama_24px.svg',
          data_source: null,
          position: self.items.length + 1
        };
        self.items.push(item);
      }
      else if(item_type==='radio'||item_type==='checkbox') {
        var item = {
          id_string: curId,
          name: 'select_control' + curId,
          type: item_type,
          width: 100,
          height: 100,
          values: 'Option 1',
          role: 'input',
          sub_type: 'div',
          layout: 'column',
          icon: null,
          data_source: null,
          position: self.items.length + 1
        };
        self.items.push(item);

      } else if (item_type === 'text_area') {

        var item = {
          id_string: curId,
          name: 'text_area_placeholder' + curId,
          type: item_type,
          width: 100,
          height: 100,
          values: 'Text placeholder',
          role: 'input',
          sub_type: 'div',
          layout: 'column',
          data_source: null,
          position: self.items.length + 1
        };
        self.items.push(item);

      } else if (item_type === 'text_field') {

        var item = {
          id_string: curId,
          name: 'text_field_placeholder' + curId,
          type: item_type,
          width: 100,
          height: 100,
          values: 'Text placeholder',
          role: 'input',
          sub_type: 'div',
          layout: 'column',
          data_source: null,
          position: self.items.length + 1
        };
        self.items.push(item);

      } else if (item_type === 'select') {

        var item = {
          id_string: curId,
          name: 'select_placeholder' + curId,
          type: item_type,
          width: 100,
          height: 100,
          values: null,
          role: 'input',
          sub_type: 'div',
          layout: 'column',
          data_source: null,
          position: self.items.length + 1
        };
        self.items.push(item);
      } else if (item_type === 'labeled_input') {
        var item = {
          id_string: curId,
          name: 'labeled_input' + curId,
          type: item_type,
          width: 100,
          height: 100,
          values: 'Label1',
          role: 'input',
          sub_type: 'h4',
          layout: 'column',
          data_source: null,
          position: self.items.length + 1
        };
        self.items.push(item);
      }
      sync();
    }

    function onOver(event, ui) {
      console.log('onOver');
    }

    function generateId() {
      return 'id' + ++idGenIndex;
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
    self.showTaskDesign = function(previewButton){
      $mdDialog.show({
      template: '<md-dialog>' +
            '<md-dialog-content>' +
            '<h3><span ng-bind="project.currentProject.name"></span></h3>' +
            '<span ng-bind="project.currentProject.description"></span>' +
            '<md-divider></md-divider>' +
            '<ul ng-model="template.items" class="no-decoration-list">' +
            '<li class="template-item" ng-repeat="item in template.items">' +
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
    };

    $scope.$on("$destroy", function() {
      Project.syncLocally($scope.project.currentProject);
    });
  }
  
})();