/**
* ProjectController
* @namespace crowdsource.project.controllers
 * @author dmorina neilthemathguy
*/
(function () {
  'use strict';

  angular
    .module('crowdsource.project.controllers')
    .controller('ProjectController', ProjectController);

  ProjectController.$inject = ['$window', '$location', '$scope', '$mdToast', 'Project',
    '$filter', '$mdSidenav', '$routeParams', 'Skill', 'Upload', 'Authentication'];

  /**
  * @namespace ProjectController
  */
  function ProjectController($window, $location, $scope, $mdToast, Project,
    $filter, $mdSidenav, $routeParams, Skill, Upload, Authentication) {
      var self = this;
      self.startDate = $filter('date')(new Date(), 'yyyy-MM-ddTHH:mmZ');
      self.addProject = addProject;
      self.endDate = $filter('date')(new Date(), 'yyyy-MM-ddTHH:mmZ');
      self.name = null;
      self.description = null;
      self.saveCategories = saveCategories;
      self.getReferenceData = getReferenceData;
      self.categories = [];
      self.getSelectedCategories = getSelectedCategories;
      self.showTemplates = showTemplates;
      self.closeSideNav = closeSideNav;
      self.finishModules = finishModules;
      self.activateTemplate = activateTemplate;
      self.addTemplate = addTemplate;
      self.addModule = addModule;
      self.getStepId = getStepId;
      self.getStepName = getStepName;
      self.getPrevious = getPrevious;
      self.getNext = getNext;
      self.upload = upload;
      self.form = {
          category: {is_expanded: false, is_done:false},
          general_info: {is_expanded: false, is_done:false},
          modules: {is_expanded: false, is_done:false},
          templates: {is_expanded: false, is_done:false},
          review: {is_expanded: false, is_done:false}
      };
      self.currentProject = Project.retrieve();
      self.currentProject.payment = self.currentProject.payment || {};
      self.toggle = toggle;
      self.selectedItems = [];
      self.isSelected = isSelected;
      self.sort = sort;
      self.config = {
          order_by: "",
          order: ""
      };

      self.myProjects = [];
      Project.getProjects().then(function(data) {
        self.myProjects = data[0];
      });

      self.getStatusName = getStatusName;
      self.monitor = monitor;

      self.other = false;
      self.otherIndex = 7;

      self.currentProject.payment.charges = 1;

      self.addDriveFolder = addDriveFolder;
      self.getFiles = getFiles;

      self.createModules = createModules;
      self.getTemplateItems = getTemplateItems;
      self.generateRandomTemplateName= generateRandomTemplateName;

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
          Project.getCategories().then(
            function success(resp) {
              var data = resp[0];
              self.categories = data;
            },
            function error(resp) {
              var data = resp[0];
              self.error = data.detail;
            }).finally(function () {});
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

          Project.addProject(self.currentProject, self.createModules()).then(
            function success(resp) {
                var data = resp[0];
                self.form.general_info.is_done = true;
                self.form.general_info.is_expanded = false;
                self.form.modules.is_expanded=true;
                Project.clean();
                $location.path('/monitor');
            },
            function error(resp) {
              var data = resp[0];
              self.error = data.detail;
          }).finally(function () {

          });
      }

      function getTemplateItems(index) {
        var template_items = angular.copy(self.currentProject.template.items);
        var new_template_items = [];
        for(var i = 0; i < template_items.length; i++) {
          var template_item = angular.copy(template_items[i]);
          if(template_item.dataSource) {
            template_item['values'] = self.currentProject.uploadedCSVData[index][template_item.dataSource];
          }
          new_template_items.push(template_item);
        }
        return new_template_items;
      }

      function createModules() {
        var modules = [];
        for(var i = 0; i < self.currentProject.uploadedCSVData.length; i++) {
          var module = 
              {
                name: 'Prototype Task',
                description: self.currentProject.prototypeTaskDescription,
                template: [
                  {
                    name: self.generateRandomTemplateName(),
                    share_with_others: true,
                    template_items: self.getTemplateItems(i)
                  }
                ],
                price: self.currentProject.payment.wage_per_hit,
                status: 1,
                repetition: self.currentProject.taskType !== "oneTask",
                number_of_hits: self.currentProject.payment.number_of_hits,
                module_timeout: 0,
                has_data_set: true,
                data_set_location: ''
              };
          modules.push(module);
        }
        return modules;
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
      function getStepId(){
          return $routeParams.projectStepId;
      }
      function getStepName(stepId){
          if(stepId==1){
              return '1. Getting Started';
          }
          else if(stepId==2){
              return '2. Project Details';
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
      function toggle(item) {
          var idx = self.selectedItems.indexOf(item);
          if (idx > -1) self.selectedItems.splice(idx, 1);
          else self.selectedItems.push(item);
      }
      function isSelected(item){
          return !(self.selectedItems.indexOf(item) < 0);
      }

      function sort(header){
          var sortedData = $filter('orderBy')(self.myProjects, header, self.config.order==='descending');
          self.config.order = (self.config.order==='descending')?'ascending':'descending';
          self.config.order_by = header;
          self.myProjects = sortedData;
      }

      function loadMyProjects() {
          Projects.getMyProjects()
              .then(function success(data, status) {
                  self.myProjects = data.data;
              },
              function error(data, status) {

              }).finally(function () {

              }
          );
      }

      function getStatusName (status) {
        return status == 1 ? 'created' : (status == 2 ? 'in review' : (status == 3 ? 'in progress' : 'completed'));
      }

      function monitor(project) {
        window.location = 'monitor/' + project.id;
      }

      function addDriveFolder(name) {
        Project.addDriveFolder(name, "").then (
          function success(data,status) {
            Project.addDriveFolder("Prototype-task", name).then (
              function success(data,status) {
                  self.prototype_task_id = data[0].id;
                  window.open("https://drive.google.com/drive/u/1/folders/" + data[0].id);

              }, function error(resp) {
                  console.log("sad times");
              });
          },
          function error(resp) {
            console.log("boooo");

          }).finally(function () {

          });
      }
      function getFiles() {
        Project.getFiles(self.prototype_task_id).then (
          function success(data, status) {
            console.log(data);
            console.log("yeeee");
          }, function error(resp) {
            console.log("boooo");
          });
      }

      function upload(files) {
        if (files && files.length) {
          var tokens = Authentication.getCookieOauth2Tokens();
          for (var i = 0; i < files.length; i++) {
            var file = files[i];
            Upload.upload({
              url: '/api/google-drive/parse-csv',
              fields: {'username': $scope.username},
              file: file,
              headers: {
                'Authorization': tokens.token_type + ' ' + tokens.access_token
              }
            }).progress(function (evt) {
              var progressPercentage = parseInt(100.0 * evt.loaded / evt.total);
              console.log('progress: ' + progressPercentage + '% ' + evt.config.file.name);
            }).success(function (data, status, headers, config) {
              self.currentProject.uploadedCSVData = data;
              self.currentProject.totalTasks = (self.currentProject.uploadedCSVData.length - 1) || 0;
              Project.syncLocally(self.currentProject);

            }).error(function (data, status, headers, config) {
              $mdToast.showSimple('Error uploading csv.');
            })
          }
        }
      }

      function generateRandomTemplateName() {
        var possible = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
        var random = _.sample(possible, 8).join('');
        return 'template_' + random;
      }
  }
})();