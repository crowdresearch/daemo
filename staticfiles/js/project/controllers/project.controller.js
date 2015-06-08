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

  ProjectController.$inject = ['$window', '$location', '$scope', 'Project', '$filter'];

  /**
  * @namespace ProjectController
  */
  function ProjectController($window, $location, $scope, Project, $filter) {
      var self = this;
      self.startDate = $filter('date')(new Date(), 'yyyy-MM-dd h:mma Z');
      self.addProject = addProject;
      self.endDate = null;
      self.name = null;
      self.description = null;
      self.categories = '';

      self.categoryPool = ('Programming Painting Design Image-Labelling Writing')
          .split(' ').map(function (category) { return { name: category }; });
      /**
       * @name addProject
       * @desc Create new project
       * @memberOf crowdsource.project.controllers.ProjectController
       */
      function addProject() {
          Project.addProject(self.name, self.startDate, self.endDate, self.description).then(
            function success(data, status) {
              //TODO
            },
            function error(data, status) {
                self.error = data.data.detail;
                //$scope.form.$setPristine();
          }).finally(function () {

              });
      }
  }
})();