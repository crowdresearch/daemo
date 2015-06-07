/**
* ProjectController
* @namespace crowdsource.project.controllers
*/
(function () {
  'use strict';

  angular
    .module('crowdsource.project.controllers')
    .controller('ProjectController', ProjectController);

  ProjectController.$inject = ['$window', '$location', '$scope', 'Project'];

  /**
  * @namespace ProjectController
  */
  function ProjectController($window, $location, $scope, Project) {
    var self = this;

    self.login = activate;

    /**
    * @name activate
    * @desc Actions to be performed when this controller is instantiated
    * @memberOf crowdsource.project.controllers.ProjectController
    */
    function activate() {

    }


  }
})();