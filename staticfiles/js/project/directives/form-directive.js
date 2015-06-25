(function () {
  'use strict';

  angular
    .module('crowdsource.project.directives')
    .directive('formDirective', formDirective);

  formDirective.$inject = [];

  /**
  * @namespace formDirective
  */
   function formDirective () {

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