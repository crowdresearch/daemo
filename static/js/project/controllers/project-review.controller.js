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
        self.submissions = [];
        self.resolvedData = {};
        self.getQuestionNumber = getQuestionNumber;
        self.hasOptions = hasOptions;
        activate();
        function activate() {
            self.resolvedData = resolvedData[0];
            if ($routeParams.projectId) {
                Task.getTasks($routeParams.projectId).then(
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
            else if ($routeParams.taskId) {
                Task.listSubmissions($routeParams.taskId).then(
                    function success(response) {
                        self.loading = false;
                        self.submissions = response[0];
                    },
                    function error(response) {
                        $mdToast.showSimple('Could not get submissions.');
                    }
                ).finally(function () {
                });
            }
        }

        function getQuestionNumber(resultObj){
            var item = $filter('filter')(self.resolvedData.template.template_items, {id: resultObj.template_item})[0];
            return item.position;
        }
        function hasOptions(item){
            return item.aux_attributes.hasOwnProperty('options');
        }
    }
})();
