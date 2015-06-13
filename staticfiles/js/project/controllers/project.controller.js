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
      self.selectedCategories = [];
      self.categories = [{name:'Programming', id:0},{name:'Painting', id:1},{name:'Design & Multimedia', id:2},
          {name:'Image Labelling', id:3},{name:'Writing', id:4}, {name:'Translation', id:5},
        {name:'Legal', id:6},{name:'Engineering', id:7}, {name:'Other', id:8}];
      self.getPath = function(){
          return $location.path();
      };
      self.toggle = function (item, list) {
        var idx = list.indexOf(item);
        if (idx > -1) list.splice(idx, 1);
        else list.push(item);
      };
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