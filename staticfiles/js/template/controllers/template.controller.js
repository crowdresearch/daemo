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

    TemplateController.$inject = ['$window', '$location', '$scope', 'Template', '$filter'];

  /**
  * @namespace TemplateController
  */
  function TemplateController($window, $location, $scope, Template, $filter) {
    var self = this;
    self.path = 'properties';
    self.selectedTab = 0;
    self.templateComponents = [
      {
        id: 1,
        name: "Label",
        icon: null,
        description: "Use for static text: labels, headings, paragraphs"
      },
      {
        id: 2,
        name: "Checkbox",
        icon: null,
        description: "Use for selecting multiple options"
      },
      {
        id: 3,
        name: "Radio Button",
        icon: null,
        description: "Use when only one option needs to be selected"
      },
      {
        id: 4,
        name: "Select list",
        icon: null,
        description: "Use for selecting multiple options from a larger set"
      },
      {
        id: 5,
        name: "Text field",
        icon: null,
        description: "Use for short text input"
      },
      {
        id: 6,
        name: "Text Area",
        icon: null,
        description: "Use for longer text input"
      },
      {
        id: 7,
        name: "Image Container",
        icon: null,
        description: "A placeholder for the image"
      },
      {
        id: 8,
        name: "Video Container",
        icon: null,
        description: "A placeholder for the video player"
      },
      {
        id: 9,
        name: "Audio Container",
        icon: null,
        description: "A placeholder for the audio player"
      }
    ];
    self.selectedItem = {
      options: "Cat,Sky,Dog",
      layout: "row"
    };
    self.options = self.selectedItem.options.split(',');

  }
  
})();