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
      self.startDate = $filter('date')(new Date(), 'yyyy-MM-ddTHH:mmZ');
      self.addProject = addProject;
      self.endDate = $filter('date')(new Date(), 'yyyy-MM-ddTHH:mmZ');
      self.name = null;
      self.description = null;
      self.selectedCategories = [];
      self.saveCategories = saveCategories;
      self.categories = [];
      self.getPath = function(){
          return $location.path();
      };
      self.toggle = function (item) {
          Project.toggle(item);
      };
      self.categoryPool = ('Programming Painting Design Image-Labelling Writing')
          .split(' ').map(function (category) { return { name: category }; });
      activate();
      function activate(){
          Project.getCategories().then(
            function success(data, status) {
                self.categories = data.data;
            },
            function error(data, status) {
                self.error = data.data.detail;
            }).finally(function () {});
      }
      /**
       * @name addProject
       * @desc Create new project
       * @memberOf crowdsource.project.controllers.ProjectController
       */
      function addProject() {
          var project = {
              name: self.name,
              startDate: self.startDate,
              endDate: self.endDate,
              description: self.description,
              keywords: self.keywords,
              categories: Project.selectedCategories
          };
          Project.addProject(project).then(
            function success(data, status) {
              //TODO
                $location.path('/milestones');
            },
            function error(data, status) {
                self.error = data.data.detail;
                console.log(Project.selectedCategories);
                //$scope.form.$setPristine();
          }).finally(function () {

              });
      }
      function saveCategories() {
          $location.path('/project');
      }
  }
})();