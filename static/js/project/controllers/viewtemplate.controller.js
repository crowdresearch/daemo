
(function () {
  'use strict';

  angular
    .module('crowdsource.project.controllers')
    .controller('ViewTemplateCtrl', ViewTemplateCtrl);

  ViewTemplateCtrl.$inject = ['$scope', 'FormService', '$routeParams'];

  /**
  * @namespace ViewTemplateCtrl
  */
  function ViewTemplateCtrl ($scope, FormService, $routeParams) {
      $scope.form = {};
    // read form with given id
    FormService.form($routeParams.id).then(function(form) {
      $scope.form = form;
    });
  }

})();