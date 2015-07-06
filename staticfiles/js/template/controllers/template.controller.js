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

    TemplateController.$inject = ['$window', '$location', '$scope', 'Template', '$filter', '$sce'];

  /**
  * @namespace TemplateController
  */
  function TemplateController($window, $location, $scope, Template, $filter, $sce) {
    var self = this;
    self.selectedTab = 0;
    self.buildHtml = buildHtml;
    self.setSelectedItem = setSelectedItem;
    self.selectedItem = null;
    $scope.onOver = onOver;
    $scope.onDrop = onDrop;
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
        name: "Video Container",
        icon: null,
        type: 'video',
        description: "A placeholder for the video player"
      },
      {
        id: 9,
        name: "Audio Container",
        icon: null,
        type: 'audio',
        description: "A placeholder for the audio player"
      }
    ];

    self.items = [
      /*{
        id: 'lbl_01',
        name: 'Question 1',
        width: 100,
        height: 100,
        values: 'What is shown in the image below?',
        type: 'label',
        role: 'display',
        sub_type: 'h4',
        layout: 'column',
        icon: null,
        data_source: null
      },
      {
        id: 'img_01',
        name: 'Image Placeholder 1',
        width: 100,
        height: 100,
        values: null,
        type: 'image',
        role: 'display',
        sub_type: null,
        layout: 'column',
        icon: '/static/bower_components/material-design-icons/image/svg/production/ic_panorama_24px.svg',
        data_source: null
      },
      {
        id: 'rg_01',
        name: 'Radio Group 1',
        width: 100,
        height: 100,
        values: 'Dog, Lion, Cat',
        type: 'checkbox',
        role: 'input',
        sub_type: null,
        layout: 'column',
        icon: null,
        data_source: null
      }*/
    ];

    function buildHtml(item) {
      var html = '';
      if (item.type === 'label') {
        html = '<' + item.sub_type + '>' + item.values + '</' + item.sub_type + '>';
      }
      else if (item.type === 'image') {
        //html = '<img class="image-container" src="'+item.icon+'">'+'</img>';
        html = '<md-icon class="image-container" md-svg-src="' + item.icon + '"></md-icon>';
      }
      else if (item.type === 'radio') {
        html = '<md-radio-group class="template-item" ng-model="item.answer" layout="' + item.layout + '">' +
            '<md-radio-button ng-repeat="option in item.values.split(\',\')" value="{{option}}">{{option}}</md-radio-button>';
      }
      else if (item.type === 'checkbox') {
        html = '<div  layout="' + item.layout + '" layout-wrap><div class="template-item" ng-repeat="option in item.values.split(\',\')" >' +
            '<md-checkbox> {{ option }}</md-checkbox></div></div> ';
      } else if (item.type === 'text_area') {
        html = '<md-input-container><textarea class="template-item" ng-model="item.answer" layout="' + item.layout + '"></textarea></md-input-container>';
      } else if (item.type === 'text_field') {
        html = '<md-input-container><input type="text" class="template-item" ng-model="item.answer" layout="' + item.layout + '"/></md-input-container>';
      } else if (item.type === 'select') {
        html = '<md-select class="template-item" ng-model="item.answer" layout="' + item.layout + '">' +
            '<md-option ng-repeat="option in item.values.split(\',\')" value="{{option}}">{{option}}</md-option></md-select>'; 
      }
      return $sce.trustAsHtml(html);
    }

    function setSelectedItem(item) {
      self.selectedItem = item;
      self.selectedTab = 1;
    }

    function onDrop(event, ui) {
      console.log('dropped');
      var item_type = $(ui.draggable).attr('data-type');
      console.log(item_type)
      if(item_type==='label') {
        var item = {
          id: 'lbl_g02',
          name: 'label',
          type: item_type,
          width: 100,
          height: 100,
          values: 'Label 1',
          role: 'display',
          sub_type: 'h4',
          layout: 'column',
          icon: null,
          data_source: null
        };
        self.items.push(item);
      }
      else if(item_type==='image') {
        var item = {
          id: 'img_g02',
          name: 'image placeholder',
          type: item_type,
          width: 100,
          height: 100,
          values: null,
          role: 'display',
          sub_type: null,
          layout: 'column',
          icon: '/static/bower_components/material-design-icons/image/svg/production/ic_panorama_24px.svg',
          data_source: null
        };
        self.items.push(item);
      }
      else if(item_type==='radio'||item_type==='checkbox') {
        var item = {
          id: 'slc_g02',
          name: 'Select Control',
          type: item_type,
          width: 100,
          height: 100,
          values: 'Option 1',
          role: 'display',
          sub_type: null,
          layout: 'column',
          icon: null,
          data_source: null
        };
        self.items.push(item);

      } else if (item_type === 'text_area') {

        var item = {
          id: 'txt_area_g02',
          name: 'text_area_placeholder',
          type: item_type,
          width: 100,
          height: 100,
          values: null,
          role: 'display',
          sub_type: null,
          layout: 'column',
          data_source: null
        };
        self.items.push(item);

      } else if (item_type === 'text_field') {

        var item = {
          id: 'txt_field_g02',
          name: 'text_field_placeholder',
          type: item_type,
          width: 100,
          height: 100,
          values: null,
          role: 'display',
          sub_type: null,
          layout: 'column',
          data_source: null
        };
        self.items.push(item);

      } else if (item_type === 'select') {

        var item = {
          id: 'select_g02',
          name: 'select_placeholder',
          type: item_type,
          width: 100,
          height: 100,
          values: null,
          role: 'display',
          sub_type: null,
          layout: 'column',
          data_source: null
        };
        self.items.push(item);
      }
    }

    function onOver(event, ui) {
      console.log('onOver');
    }
  }
  
})();