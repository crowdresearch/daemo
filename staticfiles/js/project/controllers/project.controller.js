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

  ProjectController.$inject = ['$window', '$location', '$scope', 'Project', '$filter', '$mdSidenav'];

  /**
  * @namespace ProjectController
  */
  function ProjectController($window, $location, $scope, Project, $filter, $mdSidenav) {
      var self = this;
      self.startDate = $filter('date')(new Date(), 'yyyy-MM-ddTHH:mmZ');
      self.addProject = addProject;
      self.endDate = $filter('date')(new Date(), 'yyyy-MM-ddTHH:mmZ');
      self.name = null;
      self.description = null;
      self.saveCategories = saveCategories;
      self.categories = [];
      self.getSelectedCategories = getSelectedCategories;
      self.showTemplates = showTemplates;
      self.closeSideNav = closeSideNav;
      self.finishModules = finishModules;
      self.activateTemplate = activateTemplate;
      self.addTemplate = addTemplate;
      self.addModule = addModule;
      self.module = {
          serviceCharges: 0.3,
          taskAvgTime: 5,
          minWage: 12,
          minNumOfWorkers: 1,
          workerHelloTimeout: 8,
          milestone0: {
              name: "Milestone 0",
              startDate: $filter('date')(new Date(), 'yyyy-MM-ddTHH:mmZ'),
              endDate: $filter('date')(new Date(), 'yyyy-MM-ddTHH:mmZ')
          },
          milestone1: {
              name: "Milestone 1",
              startDate: $filter('date')(new Date(), 'yyyy-MM-ddTHH:mmZ'),
              endDate: $filter('date')(new Date(), 'yyyy-MM-ddTHH:mmZ')
          }
      };

      self.modules = [
          {
              name: "Module 1",
              description: "Description of module 1",
              repetition: 3,
              dataSource: '/crowdresearch/images/*.jpg',
              startDate: $filter('date')(new Date(), 'yyyy-MM-ddTHH:mmZ'),
              endDate: $filter('date')(new Date(), 'yyyy-MM-ddTHH:mmZ'),
              workerHelloTimeout: 4,
              minNumOfWorkers: 2,
              maxNumOfWorkers: 100,
              tasksDuration: 10,
              milestone0: {
                      name: "Milestone 0",
                      description: "Complete 10 tasks",
                      allowRevision: true,
                      allowNoQualifications: false,
                      startDate: $filter('date')(new Date(), 'yyyy-MM-ddTHH:mmZ'),
                      endDate: $filter('date')(new Date(), 'yyyy-MM-ddTHH:mmZ'),
              },
              milestone1: {
                      name: "Milestone 1",
                      description: "Complete the rest of the tasks",
                      startDate: $filter('date')(new Date(), 'yyyy-MM-ddTHH:mmZ'),
                      endDate: $filter('date')(new Date(), 'yyyy-MM-ddTHH:mmZ'),
              },
              numberOfTasks: 128,
              taskPrice: 0.5

          },
          {
              name: "Module 2",
              description: "Description of module 2",
              repetition: 3,
              dataSource: '/crowdresearch/images/*.png',
              startDate: $filter('date')(new Date(), 'yyyy-MM-ddTHH:mmZ'),
              endDate: $filter('date')(new Date(), 'yyyy-MM-ddTHH:mmZ'),
              workerHelloTimeout: 6,
              minNumOfWorkers: 2,
              maxNumOfWorkers: 100,
              tasksDuration: 4,
              milestone0: {
                      name: "Milestone 0",
                      description: "Complete 6 tasks",
                      allowRevision: true,
                      allowNoQualifications: false,
                      startDate: $filter('date')(new Date(), 'yyyy-MM-ddTHH:mmZ'),
                      endDate: $filter('date')(new Date(), 'yyyy-MM-ddTHH:mmZ'),
              },
              milestone1: {
                      name: "Milestone 1",
                      description: "Complete the rest of the tasks",
                      startDate: $filter('date')(new Date(), 'yyyy-MM-ddTHH:mmZ'),
                      endDate: $filter('date')(new Date(), 'yyyy-MM-ddTHH:mmZ'),
              },
              numberOfTasks: 64,
              taskPrice: 0.8

          }
      ];

      self.form = {
          category: {is_expanded: false, is_done:false},
          general_info: {is_expanded: false, is_done:false},
          modules: {is_expanded: false, is_done:false},
          templates: {is_expanded: false, is_done:false},
          review: {is_expanded: false, is_done:false}
      };

      self.templateComponents = [
          {
              id: 1,
              name: "Label",
              icon: null
          },
          {
              id: 2,
              name: "Checkbox",
              icon: null
          },
          {
              id: 3,
              name: "Radio Button",
              icon: null
          },
          {
              id: 4,
              name: "Select list",
              icon: null
          },
          {
              id: 5,
              name: "Text field",
              icon: null
          },
          {
              id: 6,
              name: "Text Area",
              icon: null
          },
          {
              id: 7,
              name: "Image Container",
              icon: null
          },
          {
              id: 8,
              name: "Video Container",
              icon: null
          },
          {
              id: 9,
              name: "Audio Container",
              icon: null
          }
      ];
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
                self.form.general_info.is_done = true;
                self.form.general_info.is_expanded = false;
                self.form.modules.is_expanded=true;
                //$location.path('/milestones');
            },
            function error(data, status) {
                self.error = data.data.detail;
                console.log(Project.selectedCategories);
                //$scope.form.$setPristine();
          }).finally(function () {

              });
      }
      function saveCategories() {
          self.form.category.is_expanded = false;
          self.form.category.is_done=true;
          self.form.general_info.is_expanded = true;
      }

      function getSelectedCategories(){

          return Project.selectedCategories;
      }
      function showTemplates(){
          if (self.getSelectedCategories().indexOf(3) < 0) {

          } else {
              return true;
          }
      }
      function closeSideNav(){
        $mdSidenav('right').close()
        .then(function () {
        });
      }
      function finishModules(){
          self.form.modules.is_done = true;
          self.form.modules.is_expanded = false;
          if (!self.showTemplates()) {
              self.form.review.is_expanded = true;
          } else {
              self.form.templates.is_expanded = true;
          }

      }
      function activateTemplate(template){
          self.selectedTemplate = template;
      }
      function addTemplate(){
          self.form.templates.is_done = true;
          self.form.templates.is_expanded = false;
          self.form.review.is_expanded = true;
      }
      function addModule(){
          var module = {
              name: self.module.name,
              description: self.module.description,
              repetition: self.module.repetition,
              dataSource: self.module.datasource,
              startDate: self.module.startDate,
              endDate: self.module.endDate,
              workerHelloTimeout: self.module.workerHelloTimeout,
              minNumOfWorkers: self.module.minNumOfWorkers,
              maxNumOfWorkers: self.module.maxNumOfWorkers,
              tasksDuration: self.module.tasksDuration,
              milestone0: {
                      name: self.module.milestone0.name,
                      description: self.module.milestone0.description,
                      allowRevision: self.module.milestone0.allowRevision,
                      allowNoQualifications: self.module.milestone0.allowNoQualifications,
                      startDate: self.module.milestone0.startDate,
                      endDate: self.module.milestone0.endDate
              },
              milestone1: {
                      name: self.module.milestone1.name,
                      description: self.module.milestone1.description,
                      startDate: self.module.milestone1.startDate,
                      endDate: self.module.milestone1.endDate
              },
              numberOfTasks: self.module.numberOfTasks,
              taskPrice: self.module.taskPrice
          };
          self.modules.push(module);
      }
  }
})();