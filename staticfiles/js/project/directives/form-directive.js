(function () {
  'use strict';

  angular
    .module('crowdsource.project.controllers')
    .controller('formDirective', formDirective);

  formDirective.$inject = [];

  /**
  * @namespace formDirective
  */
   function formDirective ($http, $compile) {

    return {
      controller: function($scope){
          $scope.submit = function(){
              alert('Form submitted..');
              $scope.form.submitted = true;
          }

          $scope.cancel = function(){
              alert('Form canceled..');
          }
      },
      templateUrl: '/static/templates/project/directive-templates/form/form.html',
      restrict: 'E',
      scope: {
          form:'='
      }
    };

  }

})();