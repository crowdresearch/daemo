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
        self.getDate = getDate;
        self.getTaskNumber = getTaskNumber;
        self.deleteProject = deleteProject;
        self.projectToDelete = null;
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
            $state.go('project_rating', {projectId: project_id});
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
                    $mdToast.showSimple(response[0][0] + '. Open the project to edit it.');
                }
            ).finally(function () {
            });
        }

        function discard(item, $event) {
            var parent = angular.element(document.body);
            self.projectToDelete = item;
            $mdDialog.show({
                clickOutsideToClose: true,
                scope: $scope,
                preserveScope: true,
                parent: parent,
                targetEvent: $event,
                templateUrl: '/static/templates/project/delete.html',
                controller: DialogController
            });
        }

        function deleteProject() {
            Project.deleteInstance(self.projectToDelete.id).then(
                function success(response) {
                    self.myProjects.splice(self.myProjects.findIndex(function (element, index, array) {
                        return element.id == self.projectToDelete.id;
                    }), 1);
                    $mdToast.showSimple('Deleted ' + self.projectToDelete.name + '.');
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

        function getDate(timestamp) {
            return new Date(timestamp).toLocaleString();
        }

        function getTaskNumber(rawNUmber, numberOfRevisions, status) {
            if (status == self.status.STATUS_DRAFT && numberOfRevisions == 1 && rawNUmber == 0) {
                return '-';
            }
            return rawNUmber;
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
