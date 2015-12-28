(function () {
    'use strict';

    angular
        .module('crowdsource.project.controllers')
        .controller('ProjectReviewController', ProjectReviewController);

    ProjectReviewController.$inject = ['$scope', 'Project', 'resolvedData', '$routeParams', 'Task', '$mdToast',
        '$filter'];

    /**
     * @namespace ProjectReviewController
     */
    function ProjectReviewController($scope, Project, resolvedData, $routeParams, Task, $mdToast, $filter) {
        var self = this;
        self.tasks = [];
        self.loading = true;
        self.loadingSubmissions = true;
        self.submissions = [];
        self.resolvedData = {};
        self.getQuestionNumber = getQuestionNumber;
        self.hasOptions = hasOptions;
        self.listSubmissions = listSubmissions;
        self.isSelected = isSelected;
        self.selectedTaskId = null;
        self.taskData = null;
        self.selectedTask = {}
        self.toggleSelected = toggleSelected;

        activate();
        function activate() {
            self.resolvedData = resolvedData[0];
            Task.getTasks(self.resolvedData.id).then(
                function success(response) {
                    self.loading = false;
                    self.tasks = response[0];
                },
                function error(response) {
                    $mdToast.showSimple('Could not get tasks.');
                }
            ).finally(function () {
            });
        }

        function listSubmissions(task) {
            Task.retrieve(task.id).then(
                function success(response) {
                    self.taskData = response[0];
                    //self.selectedTaskId = task_id;
                    //self.loadingSubmissions = false;
                },
                function error(response) {
                    $mdToast.showSimple('Could not get submissions.');
                }
            ).finally(function () {
            });
            Task.listSubmissions(task.id).then(
                function success(response) {
                    self.submissions = response[0];
                    self.selectedTask = task;
                    self.loadingSubmissions = false;
                },
                function error(response) {
                    $mdToast.showSimple('Could not get submissions.');
                }
            ).finally(function () {
            });
        }

        function getQuestionNumber(resultObj) {
            var item = $filter('filter')(self.resolvedData.templates[0].template_items, {id: resultObj.template_item})[0];
            return item.position;
        }

        function hasOptions(item) {
            return item.aux_attributes.hasOwnProperty('options');
        }

        function isSelected(task) {
            return angular.equals(task, self.selectedTask);
        }
        function toggleSelected(item){
            if(angular.equals(item, self.selectedTask)){
                self.selectedTask = null;
                self.submissions = [];
                self.taskData = null;
                self.loadingSubmissions = true;
            }
            else {
                self.listSubmissions(item);
            }
        }
    }
})();
