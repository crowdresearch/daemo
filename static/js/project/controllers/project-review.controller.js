(function () {
    'use strict';

    angular
        .module('crowdsource.project.controllers')
        .controller('ProjectReviewController', ProjectReviewController);

    ProjectReviewController.$inject = ['$scope', 'Project', 'projectData', '$routeParams', 'Task', '$mdToast'];

    /**
     * @namespace ProjectReviewController
     */
    function ProjectReviewController($scope, Project, projectData, $routeParams, Task, $mdToast) {
        var self = this;
        self.tasks = [];
        activate();
        function activate() {
            self.projectData = projectData[0];
            if ($routeParams.projectId) {
                Task.getTasks($routeParams.projectId).then(
                    function success(response) {
                        self.tasks = response[0];
                    },
                    function error(response) {
                        $mdToast.showSimple('Could not get tasks.');
                    }
                ).finally(function () {
                });
            }
        }


    }
})();
