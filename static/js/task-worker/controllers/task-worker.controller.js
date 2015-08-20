
(function () {
  'use strict';

  angular
    .module('crowdsource.task-worker.controllers')
    .controller('taskWorkerDetailController', taskWorkerDetailController);

	taskWorkerDetailController.$inject = ['$scope', '$sce', '$location', '$mdToast', '$log', '$http',
    '$routeParams', 'Authentication', 'TaskWorker', 'TaskService'];

	function taskWorkerDetailController($scope, $sce, $location, $mdToast, $log, $http, $routeParams,
    Authentication, TaskWorker, TaskService) {	
  	
    var self = this;
    self.userAccount = Authentication.getAuthenticatedAccount();
    if (!self.userAccount) {
      $location.path('/login');
      return;
    }

    var taskWorkerId = $routeParams.taskWorkerId;
    self.task = {};
    self.results = {};

    TaskWorker.getTaskWorker(taskWorkerId).then(
      function success(resp) {
        var data = resp[0]
        var taskId = data.task;

        // Need task to get form data.
        TaskService.getTask(taskId).then(
          function success (resp) {
            var data = resp[0];
            self.moduleId = data.module;
            TaskService.getModule(self.moduleId).then(
              function success (nresp) {
                var nData = nresp[0];
                self.module = nData;
                console.log(self.module);
              }, function error (nerr) {
                $mdToast.showSimple('Error loading task.');
              });
          },
          function error (resp) {
            var data = resp[0];
            $mdToast.showSimple('Could not get task.');

          }).finally(function () {
          });

      },
      function error (resp) {

        $mdToast.showSimple('Could not retrieve this task.');

      }).finally(function () {
        self.task = {"id": 1, "milestoneDescription": "this is a milestone description", "payment":{"number_of_hits":"10","total":"6.00","wage_per_hit":"0.5","charges":"1"},"selectedCategories":[0,3,4],"name":"Sample project 1","description":"This is my sample description","taskType":"oneTask","upload":"noFile","onetaskTime":"1 hour","template":{"name":"template_bMuDT98e","items":[{"id":"id1","name":"label","type":"label","width":100,"height":100,"values":"Enter Name","role":"display","sub_type":"h4","layout":"column","icon":null,"data_source":null},{"id":"id2","name":"text_field_placeholder1","type":"text_field","width":100,"height":100,"values":null,"role":"display","sub_type":null,"layout":"column","data_source":null},{"id":"id3","name":"label","type":"label","width":100,"height":100,"values":"Enter Place of Birth","role":"display","sub_type":"h4","layout":"column","icon":null,"data_source":null},{"id":"id4","name":"text_field_placeholder2","type":"text_field","width":100,"height":100,"values":null,"role":"display","sub_type":null,"layout":"column","data_source":null},{"id":"id5","name":"label","type":"label","width":100,"height":100,"values":"Favorite Quote","role":"display","sub_type":"h4","layout":"column","icon":null,"data_source":null},{"id":"id6","name":"text_area_placeholder1","type":"text_area","width":100,"height":100,"values":null,"role":"display","sub_type":null,"layout":"column","data_source":null}]}};
      });
    



    self.buildFormEntry = function(item) {
      var html = '';
      if (item.type === 'label') {
        html = '<' + item.sub_type + '>' + item.values + '</' + item.sub_type + '>';
      }
      else if (item.type === 'image') {
        html = '<md-icon class="image-container" md-svg-src="' + item.icon + '"></md-icon>';
      }
      else if (item.type === 'radio') {
        html = '<md-radio-group class="template-item" ng-model="taskWorkerDetail.results.' + item.name + '" layout="' + item.layout + '">' +
            '<md-radio-button ng-repeat="option in item.values.split(\',\')" value="{{option}}">{{option}}</md-radio-button>';
      }
      else if (item.type === 'checkbox') {
        html = '<div  layout="' + item.layout + '" ng-model="taskWorkerDetail.results.' + item.name + '" layout-wrap><div class="template-item" ng-repeat="option in item.values.split(\',\')" >' +
            '<md-checkbox> {{ option }}</md-checkbox></div></div> ';
      } else if (item.type === 'text_area') {
        html = '<md-input-container><textarea class="template-item" ng-model="taskWorkerDetail.results.' + item.name + '" layout="' + item.layout + '"></textarea></md-input-container>';
      } else if (item.type === 'text_field') {
        html = '<md-input-container><input type="text" class="template-item" ng-model="taskWorkerDetail.results.' + item.name + '" layout="' + item.layout + '"/></md-input-container>';
      } else if (item.type === 'select') {
        html = '<md-select class="template-item" ng-model="taskWorkerDetail.results.' + item.name + '" layout="' + item.layout + '">' +
            '<md-option ng-repeat="option in item.values.split(\',\')" value="{{option}}">{{option}}</md-option></md-select>'; 
      }
      return $sce.trustAsHtml(html);
    };

    self.submitForm = function () {
      if (!$scope.taskAttemptForm.$valid) {
        $mdToast.showSimple('Form invalid!');
        return;
      }
      TaskWorker.submitResult(taskWorkerId, self.results).then(
        function success (resp) {

        }, function error (resp) {

        }).finally(function () {
          $mdToast.showSimple('Submitted!');
          $location.path('/task-feed');
        });
    };

	}

})();


