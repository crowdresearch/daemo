/**
* ProjectController
* @namespace crowdsource.project.controllers
 * @author dmorina
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

    self.addProject = addProject;

    /**
    * @name addProject
    * @desc Create new project
    * @memberOf crowdsource.project.controllers.ProjectController
    */
    function addProject(name, description, details) {
      Project.addProject(name, description, details).then(
          function success(data, status) {
              //TODO
          },
          function error(data, status) {
            vm.error = data.data.detail;
            //$scope.form.$setPristine();
          }).finally(function () {
      });
    }


  }
})();