(function () {
    'use strict';

    angular
        .module('crowdsource.project.controllers')
        .controller('MyProjectController', MyProjectController);

    MyProjectController.$inject = ['$window', '$state', '$scope', '$mdToast', 'Project',
        '$filter', 'Authentication', '$mdDialog'];

    /**
     * @namespace MyProjectController
     */
    function MyProjectController($window, $state, $scope, $mdToast, Project,
                                 $filter, Authentication, $mdDialog) {
        var self = this;
        self.myProjects = [];
        self.createProject = createProject;
        self.navigateToTasks = navigateToTasks;
        self.statusToString = statusToString;
        self.updateStatus = updateStatus;
        self.openPreferences = openPreferences;
        self.discard = discard;
        self.edit = edit;
        self.fork = fork;
        self.sort = sort;
        self.editProject = editProject;
        self.config = {
            order_by: "",
            order: ""
        };
        self.status = {
            STATUS_DRAFT: 1,
            STATUS_IN_PROGRESS: 3,
            STATUS_COMPLETED: 4,
            STATUS_PAUSED: 5
        };
        self.openActionsMenu = openActionsMenu;
        self.showPaused = showPaused;

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
                    $state.go('create_edit_project', {projectId: project_pk});
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

        function statusToString(status, revisions) {
            if (status == self.status.STATUS_DRAFT && revisions.length == 1)
                return "Not yet launched";
            else if (status == self.status.STATUS_IN_PROGRESS) {
                return "Running";
            }
            else if (self.status.STATUS_PAUSED || (self.status.STATUS_DRAFT &&
                revisions.length > 1)) {
                return "Paused";
            }
            else if (status == self.status.STATUS_COMPLETED) {
                return "Completed";
            }
            return "";
        }

        function updateStatus(item, status) {
            Project.updateStatus(item.id, {status: status}).then(
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
            $state.go('create_edit_project', {projectId: item.id});
        }

        function fork(item) {
            Project.fork(item.id).then(
                function success(response) {
                    $state.go('create_edit_project', {projectId: response[0].id});
                },
                function error(response) {
                    $mdToast.showSimple('Could not fork project.');
                }
            ).finally(function () {
            });
        }

        function openPreferences($event) {
            $mdDialog.show({
                clickOutsideToClose: true,
                scope: $scope,
                preserveScope: true,
                //parent: parent,
                targetEvent: $event,
                templateUrl: '/static/templates/project/preferences.html',
                controller: DialogController
            });
        }

        function openActionsMenu($mdOpenMenu, ev) {
            $mdOpenMenu(ev);
        }

        function editProject(project_id) {
            $state.go('create_edit_project', {projectId: project_id});
        }

        function showPaused(project) {
            return project.status == self.status.STATUS_PAUSED
                || (project.status == self.status.STATUS_DRAFT && project.revisions.length > 1);

        }

    }


    function DialogController($scope, $mdDialog) {
        $scope.hide = function () {
            $mdDialog.hide();
        };
        $scope.cancel = function () {
            $mdDialog.cancel();
        };
    }


})();
