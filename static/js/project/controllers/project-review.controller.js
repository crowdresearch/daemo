(function () {
    'use strict';

    angular
        .module('crowdsource.project.controllers')
        .controller('ProjectReviewController', ProjectReviewController);

    ProjectReviewController.$inject = ['$scope', 'Project', 'resolvedData', '$routeParams', 'Task', '$mdToast'];

    /**
     * @namespace ProjectReviewController
     */
    function ProjectReviewController($scope, Project, resolvedData, $routeParams, Task, $mdToast) {
        var self = this;
        self.tasks = [];
        self.loading = true;
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
        }


    }
})();
