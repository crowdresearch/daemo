/**
* Project
* @namespace crowdsource.template.services
*/
(function () {
  'use strict';

  angular
    .module('crowdsource.template.services')
    .factory('Template', Template);

  Template.$inject = ['$cookies', '$http', '$q', '$location', 'HttpService'];

  /**
  * @namespace Template
  * @returns {Factory}
  */

  function Template($cookies, $http, $q, $location, HttpService) {
    /**
    * @name Template
    * @desc The Factory to be returned
    */
    var Template = {
      getCategories: getCategories,
      buildHtml: buildHtml
    };

    return Template;

    function getCategories(){
      return $http({
        url: '/api/category/',
        method: 'GET'
      });
    }

    function buildHtml(item) {
      var html = '';
      if (item.type === 'label') {
        html = '<' + item.sub_type + ' style="word-wrap:break-word">' + item.values + '</' + item.sub_type + '>';
      }
      else if (item.type === 'image') {
        html = '<img class="image-container" src="'+item.values+'">'+'</img>';
      }
      else if (item.type === 'radio') {
        html = '<md-radio-group class="template-item" ng-model="item.answer" layout="' + item.layout + '">' +
            '<md-radio-button ng-repeat="option in item.values.split(\',\')" value="{{option}}">{{option}}</md-radio-button>';
      }
      else if (item.type === 'checkbox') {
        html = '<div  layout="' + item.layout + '" layout-wrap><div class="template-item" ng-repeat="option in item.values.split(\',\')" >' +
            '<md-checkbox> {{ option }}</md-checkbox></div></div> ';
      } else if (item.type === 'text_area') {
        html = '<md-input-container><label>'+item.values+'</label><textarea class="template-item" ng-model="item.answer" layout="' + item.layout + '"></textarea></md-input-container>';
      } else if (item.type === 'text_field') {
        html = '<md-input-container><label>'+item.values+'</label><input type="text" class="template-item" ng-model="item.answer" layout="' + item.layout + '"/></md-input-container>';
      } else if (item.type === 'select') {
        html = '<md-select class="template-item" ng-model="item.answer" layout="' + item.layout + '">' +
            '<md-option ng-repeat="option in item.values.split(\',\')" value="{{option}}">{{option}}</md-option></md-select>';
      } else if (item.type === 'labeled_input') {
        html = '<div layout="row" style="word-wrap:break-word"><' + item.sub_type + ' flex="75" layout="column">' + item.values + '</' +
                item.sub_type + '><md-input-container flex="25" layout="column">' +
                '<label>Enter text here</label>' +
                '<input type="text" class="ranking-item" ng-model="item.answer">' +
                '</md-input-container></div>';
      }
      else if (item.type === 'audio'){
        html = '<audio src="'+item.values+'" controls> <p>Your browser does not support the <code>audio</code> element.</p> </audio>';
      }
      return html;
    }
  }
})();