(function () {
  'use strict';

  angular
    .module('crowdsource.project.controllers')
    .controller('ProjectController', ProjectController);

  ProjectController.$inject = ['$window', '$location', '$scope', '$mdToast', 'Project',
    '$filter', '$mdSidenav', '$routeParams', 'Skill', 'Upload', 'Authentication', 'helpersService'];

  /**
  * @namespace ProjectController
  */
  function ProjectController($window, $location, $scope, $mdToast, Project,
    $filter, $mdSidenav, $routeParams, Skill, Upload, Authentication, helpersService) {
      var self = this;
      self.addProject = addProject;
      self.name = null;
      self.description = null;
      self.getReferenceData = getReferenceData;
      self.categories = [];
      self.getSelectedCategories = getSelectedCategories;
      self.getStepId = getStepId;
      self.getStepName = getStepName;
      self.getPrevious = getPrevious;
      self.getNext = getNext;
      self.upload = upload;

      self.currentProject = Project.retrieve();
      self.currentProject.microFlag = 'micro';
      self.currentProject.payment = self.currentProject.payment || {};

      self.querySearch = function(query) {
        return helpersService.querySearch(self.currentProject.metadata.column_headers, query, false);
      };
      self.currentProject.isMicro = (self.currentProject.microFlag === "micro");
      self.currentProject.isMacro = (self.currentProject.microFlag === "macro");

      self.other = false;
      self.otherIndex = 7;

      self.currentProject.payment.charges = 1;

      self.getPath = function(){
          return $location.path();
      };
      self.toggle = function (item) {
        self.currentProject.categories = [item.id];
        if (item == self.otherIndex) self.other = true;
        else self.other = false;
      };

      self.exists = function (item) {
        var list = self.currentProject.categories || [];
        return list.indexOf(item) > -1;
      };

      activate();
      function activate(){
        if($location.$$path === '/create-project/1') {
          Project.getCategories().then(
            function success(resp) {
              var data = resp[0];
              self.categories = data;
            },
            function error(resp) {
              var data = resp[0];
              self.error = data.detail;
            }
          ).finally(function () {});
        }
      }
      function getReferenceData() {
        Project.getReferenceData().success(function(data) {
          $scope.referenceData = data[0];
        });
      }
      /**
       * @name addProject
       * @desc Create new project
       * @memberOf crowdsource.project.controllers.ProjectController
       */
      function addProject() {

        if (!self.currentProject.template || !self.currentProject.template.name) {
          $mdToast.showSimple('You haven\'t created a template.');
          return;
        }

        Project.addProject(self.currentProject).then(
          function success(resp) {
              Project.clean();
              $location.path('/monitor');
          },
          function error(resp) {
            var data = resp[0];
            self.error = data;
            $mdToast.showSimple(JSON.stringify(self.error));
        }).finally(function () {

        });
      }

      function getSelectedCategories(){

          return Project.selectedCategories;
      }

      function getStepId(){
          return $routeParams.projectStepId;
      }
      function getStepName(stepId){
          if(stepId==1){
              return '1. Category';
          }
          else if(stepId==2){
              return '2. Description';
          }
          else if(stepId==3){
              return '3. Prototype Task';
          }
          else if(stepId==4){
              return '4. Design';
          }
          else if(stepId==5){
              return '5. Payment';
          }
          else if(stepId==6){
              return '6. Summary';
          }
      }
      function getPrevious(){
          return parseInt(self.getStepId())-1;
      }
      function getNext(){
          return parseInt(self.getStepId())+1;
      }

      function computeTotal(payment) {
        var total = ((payment.number_of_hits*payment.wage_per_hit));
        if (self.currentProject.totalTasks) {
          total *= self.currentProject.totalTasks;
        }
        total = total  + payment.charges*1;
        total = total ? total.toFixed(2) : 'Error';
        return total;
      }

      $scope.$watch('project.currentProject.payment', function (newVal, oldVal) {
        if (!angular.equals(newVal, oldVal)) {
          self.currentProject.payment.total = computeTotal(self.currentProject.payment);
        }
        
      }, true);

      $scope.$on("$destroy", function() {
        Project.syncLocally(self.currentProject);
      });

      function upload(files) {
        if (files && files.length) {
          var tokens = Authentication.getCookieOauth2Tokens();
          for (var i = 0; i < files.length; i++) {
            var file = files[i];
            Upload.upload({
              url: '/api/requesterinputfile/get-metadata-and-save',
              fields: {'username': $scope.username},
              file: file,
              headers: {
                'Authorization': tokens.token_type + ' ' + tokens.access_token
              }
            }).progress(function (evt) {
              var progressPercentage = parseInt(100.0 * evt.loaded / evt.total);
              console.log('progress: ' + progressPercentage + '% ' + evt.config.file.name);
            }).success(function (data, status, headers, config) {
              self.currentProject.metadata = data.metadata;
              Project.syncLocally(self.currentProject);
            }).error(function (data, status, headers, config) {
              $mdToast.showSimple('Error uploading csv.');
            })
          }
        }
      }
  }
})();