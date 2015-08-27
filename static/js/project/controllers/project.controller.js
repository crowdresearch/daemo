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
      self.addMilestone = addMilestone;
      self.name = null;
      self.description = null;
      self.getReferenceData = getReferenceData;
      self.categories = [];
      self.getSelectedCategories = getSelectedCategories;
      self.getStepId = getStepId;
      self.getProjectId = getProjectId;
      self.getStepName = getStepName;
      self.getStepMilestone = getStepMilestone;
      self.getPrevious = getPrevious;
      self.getLastMilestone = getLastMilestone;
      self.getNext = getNext;
      self.upload = upload;
      self.initMicroFlag = initMicroFlag;

      self.currentProject = Project.retrieve();
      self.currentProject.payment = self.currentProject.payment || {};

      //work submit
      self.filesToUpload = [];
      self.uploadedFiles=[];
      self.taskInfo = "Task information will be displayed here...";
      self.uploadComment = "";


      self.querySearch = function(query) {
        return helpersService.querySearch(self.currentProject.metadata.column_headers, query, false);
      };

      self.other = false;
      self.otherIndex = 7;

      self.currentProject.payment.charges = 1;

      function initMicroFlag() {
        if(self.currentProject.microFlag == undefined) {
          self.currentProject.microFlag = 'micro';
        }
      }
      initMicroFlag();

      function getLastMilestone() {
        Project.getLastMilestone(getProjectId()).then(
          function success(resp) {
            var data = resp[0];
            self.currentProject.taskDescription = data.description;
            self.currentProject.template = {
              name: data.template[0].name,
              items: data.template[0].template_items
            }
            self.currentProject.payment = {
              number_of_hits: data.repetition,
              wage_per_hit: data.price
            }
          },
          function error(resp) {
            var data = resp[0];
            self.error = data.detail;
            $mdToast.showSimple('Could not get last milestone.');
          }
        ).finally(function () {})
      }


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
              $mdToast.showSimple('Could not get categories.');
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

      function addMilestone() {
        Project.addMilestone(self.currentProject, getProjectId()).then(
          function success(resp) {
            Project.clean();
            $location.path('/monitor');
          },
          function error(resp) {
            var data = resp[0];
            self.error = data;
            $mdToast.showSimple(JSON.stringify(self.error));
        }).finally(function () {});
      }

      function getSelectedCategories(){

          return Project.selectedCategories;
      }

      function getProjectId() {
        return $routeParams.projectId;
      }

      function getStepId(){
          return $routeParams.stepId;
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

      function getStepMilestone(stepId){
          if(stepId==1){
              return '1. Milestone';
          }
          else if(stepId==2){
              return '2. Design';
          }
          else if(stepId==3){
              return '3. Payment';
          }
          else if(stepId==4){
              return '4. Summary';
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
          //var tokens = Authentication.getCookieOauth2Tokens();
          for (var i = 0; i < files.length; i++) {
            var file = files[i];
            Upload.upload({
              url: '/api/csvmanager/get-metadata-and-save',
              fields: {'username': $scope.username},
              file: file/*,
              headers: {
                'Authorization': tokens.token_type + ' ' + tokens.access_token
              }*/
            }).progress(function (evt) {
              var progressPercentage = parseInt(100.0 * evt.loaded / evt.total);
              console.log('progress: ' + progressPercentage + '% ' + evt.config.file.name);
            }).success(function (data, status, headers, config) {
              self.currentProject.metadata = data.metadata;
              if(self.currentProject.microFlag === 'micro') {
                self.currentProject.totalTasks = self.currentProject.metadata.num_rows;
              }
              Project.syncLocally(self.currentProject);
            }).error(function (data, status, headers, config) {
              $mdToast.showSimple('Error uploading csv.');
            })
          }
        }
      }

      // watch filesToUpload and upload multiple files in any format by calling uploadViaFileManager
      $scope.$watch('project.filesToUpload',
        function (newVal, oldVal) {
          // won't upload if the file is already uploaded
          if (newVal && newVal.length) {
            for (var i = 0; i < newVal.length; i++) {
              var file = newVal[i];

              var isNewFile = true;
              for (var j=0; j < self.uploadedFiles.length; j++) {
                if (self.uploadedFiles[j].name == file.name) {
                  isNewFile = false;
                  break;
                }
              }

              if (isNewFile) {
                self.uploadViaFileManager(file);
              }
            }
          }
        },
        true
      );

      // upload single file via filemanager
      self.uploadViaFileManager = function (file) {
        Upload.upload({
          url: '/api/filemanager/',
          file: file
        }).progress(function (evt) {
          var progressPercentage = parseInt(100.0 * evt.loaded / evt.total);
          console.log('progress: ' + progressPercentage + '% ' + evt.config.file.name);
        }).success(function (data, status, headers, config) {
          // $mdToast.showSimple('file ' + config.file.name + 'uploaded. Response: ' + data);
          console.log('file ' + config.file.name + 'uploaded. Response: ' +  JSON.stringify(data));
          self.uploadedFiles.push({ name: config.file.name, size: config.file.size, timestamp: new Date(), id: data});
        }).error(function(data, status, headers, config) {
          $mdToast.showSimple('Error uploading ' + config.file.name);
        });
      };

      // remove uploaded file from the server and uploadedFiles
      self.removeUploadedFile = function (file) {
        var index = self.uploadedFiles.indexOf(file);
        if (index !== -1) {
          Project.removeUploadedFile(file.id);
          self.uploadedFiles.splice(index, 1);
        }
      }

      // remove all files in uploadedFiles from the server
      self.removeAllUploadedFiles = function () {
        for (var i=0; i < self.uploadedFiles.length; i++) {
          Project.removeUploadedFile(self.uploadedFiles[i].id);
        }
        self.uploadedFiles=[];
      }

      // cancel submit work, remove all files already uploaded
      self.cancelWork = function ($event) {
        self.removeAllUploadedFiles();
        $mdToast.showSimple('Cancelled: ' + self.uploadComment);
      };

      // do submit work
      // TODO: need to associate uploaded files to project/task
      self.submitWork = function ($event) {
        var idList = [];
        for (var i=0; i < self.uploadedFiles.length; i++) {
          idList.push(self.uploadedFiles[i].id);
        }
        $mdToast.showSimple('Submitted RequesterInputFile[' + idList.join(',') + ']: ' + self.uploadComment);
      };

    }
})();