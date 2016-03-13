(function () {
    'use strict';

    angular
        .module('crowdsource.project.controllers')
        .controller('MyProjectController', MyProjectController);

    MyProjectController.$inject = ['$window', '$state', '$scope', '$mdToast', 'Project',
        '$filter', 'Authentication'];

    /**
     * @namespace MyProjectController
     */
    function MyProjectController($window, $state, $scope, $mdToast, Project,
                                 $filter, Authentication) {
        var self = this;
        self.myProjects = [];
        self.createProject = createProject;
        self.navigateToTasks = navigateToTasks;
        self.statusToString = statusToString;
        self.updateStatus = updateStatus;
        self.discard = discard;
        self.edit = edit;
        self.fork = fork;
        self.sort = sort;
        self.config = {
            order_by: "",
            order: ""
        };

        activate();
        function activate() {
            Project.getRequesterProjects().then(
                function success(response) {
                    self.myProjects = response[0];
                },
                function error(response) {
                    $mdToast.showSimple('Could not get requester projects.');
                }
            ).finally(function () {
                });
        }

        function getStatusName(status) {
            return status == 1 ? 'created' : (status == 2 ? 'in review' : (status == 3 ? 'in progress' : 'completed'));
        }

        function toggle(item) {
            var idx = self.selectedItems.indexOf(item);
            if (idx > -1) self.selectedItems.splice(idx, 1);
            else self.selectedItems.push(item);
        }

        function isSelected(item) {
            return !(self.selectedItems.indexOf(item) < 0);
        }

        function sort(header) {
            var sortedData = $filter('orderBy')(self.myProjects, header, self.config.order === 'descending');
            self.config.order = (self.config.order === 'descending') ? 'ascending' : 'descending';
            self.config.order_by = header;
            self.myProjects = sortedData;
        }

        function createProject() {
            Project.create().then(
                function success(response) {
                    var project_pk = response[0].id;
                    $state.go('create_project', {projectId: project_pk});
                },
                function error(response) {
                    $mdToast.showSimple('Could not get requester projects.');
                }
            ).finally(function () {
                });
        }

        function navigateToTasks(project_id) {
            $state.go('project_review', {projectId: project_id});
        }

        function statusToString(status) {
            switch (status) {
                case 2:
                    return "Published";
                case 3:
                    return "In Progress";
                case 4:
                    return "Completed";
                case 5:
                    return "Paused";
                default:
                    return "Saved";
            }
        }

        function updateStatus(item, status) {
            Project.update(item.id, {status: status}, 'project').then(
                function success(response) {
                    $mdToast.showSimple('Updated ' + item.name + '!');
                    item.status = status;
                },
                function error(response) {
                    $mdToast.showSimple('Could not update project.');
                }
            ).finally(function () {
                });
        }

        function discard(item) {
            Project.deleteInstance(item.id).then(
                function success(response) {
                    self.myProjects.splice(self.myProjects.findIndex(function (element, index, array) {
                        return element.id == item.id;
                    }), 1);
                    $mdToast.showSimple('Deleted ' + item.name + '.');
                },
                function error(response) {
                    $mdToast.showSimple('Could not delete project.');
                }
            ).finally(function () {
                });
        }

        function edit(item) {
            $state.go('create_project', {projectId: item.id});
        }

        function fork(item) {
            Project.fork(item.id).then(
                function success(response) {
                    $state.go('create_project', {projectId: response[0].id});
                },
                function error(response) {
                    $mdToast.showSimple('Could not fork project.');
                }
            ).finally(function () {
                });
        }
    }
})();
