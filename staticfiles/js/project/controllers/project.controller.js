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
      self.addPayment = addPayment;
      self.endDate = $filter('date')(new Date(), 'yyyy-MM-ddTHH:mmZ');
      self.name = null;
      self.description = null;
      self.selectedCategories = [];
      self.saveCategories = saveCategories;
      self.getReferenceData = getReferenceData;
      self.categories = [];
      self.form = {
          category: {is_expanded: true, is_done:false},
          general_info: {is_expanded: false, is_done:false},
          modules: {is_expanded: false, is_done:false},
          payment: {is_expanded: false, is_done:false},
          review: {is_expanded: false, is_done:false}
      };
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
      function getReferenceData() {
        Project.getReferenceData().success(function(data) {
          $scope.referenceData = data;
        });
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
      function addPayment() {
        var payment = $scope.payment;
        var paymentObject = {
          name: self.name,
          number_of_hits: payment.hits,
          wage_per_hit: payment.wage,
          total: payment.total,
          charges: payment.charges
        }
        Project.addPayment(paymentObject).then(
          function success(data, status) {
            alert(data);
          });
      }
      function saveCategories() {
          self.form.category.is_expanded = false;
          self.form.category.is_done=true;
          self.form.general_info.is_expanded = true;
      }
  }
})();