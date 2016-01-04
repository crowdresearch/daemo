(function () {
    'use strict';

    angular
        .module('crowdsource.project.controllers')
        .controller('MyTasksController', MyTasksController);

    MyTasksController.$inject = ['$scope', 'Project', '$routeParams', 'Task', '$mdToast',
        '$filter'];

    /**
     * @namespace MyTasksController
     */
    function MyTasksController($scope, Project, $routeParams, Task, $mdToast, $filter) {
        var self = this;
        self.projects = [];
        self.loading = true;
        self.isSelected = isSelected;
        self.selectedProject = null;
        self.setSelected = setSelected;
        self.getStatus = getStatus;
        self.listMyTasks = listMyTasks;
        self.tasks = [];
        self.status = {
            RETURNED: 5,
            REJECTED: 4,
            ACCEPTED: 3,
            SUBMITTED: 2,
            IN_PROGRESS: 1
        };
        activate();
        function activate() {
            Project.listWorkerProjects().then(
                function success(response) {
                    self.loading = false;
                    self.projects = response[0];
                },
                function error(response) {
                    $mdToast.showSimple('Could not get tasks.');
                }
            ).finally(function () {
            });
        }


        function isSelected(project) {
            return angular.equals(project, self.selectedProject);
        }

        function setSelected(item) {
            self.selectedProject = item;
        }


        function getStatus(statusId) {
            for (var key in self.status) {
                if (self.status.hasOwnProperty(key)) {
                    if (statusId == self.status[key])
                        return key;
                }

            }
        }

        function listMyTasks(project) {
            Task.listMyTasks(project.id).then(
                function success(response) {
                    self.tasks = response[0].tasks;
                    self.selectedProject = project;
                },
                function error(response) {
                    $mdToast.showSimple('Could fetch project tasks');
                }
            ).finally(function () {
            });
        }


    }
})();
