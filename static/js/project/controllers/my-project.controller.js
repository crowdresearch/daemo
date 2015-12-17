(function () {
    'use strict';

    angular
        .module('crowdsource.project.controllers')
        .controller('MyProjectController', MyProjectController);

    MyProjectController.$inject = ['$window', '$location', '$scope', '$mdToast', 'Project',
        '$filter', '$routeParams', 'Authentication'];

    /**
     * @namespace MyProjectController
     */
    function MyProjectController($window, $location, $scope, $mdToast, Project,
                               $filter, $routeParams, Authentication) {
        var self = this;
        self.myModules = [];
        self.createProject = createProject;
        self.navigateToTasks = navigateToTasks;
        self.statusToString = statusToString;
        self.resume = resume;
        self.pause = pause;
        self.discard = discard;
        self.edit = edit;
        self.fork = fork;
        self.sort = sort;
        self.config = {
            order_by: "",
            order: ""
        };

        activate();
        function activate(){
            Project.getRequesterModules().then(
                function success(response) {
                    self.myModules = response[0];
                },
                function error(response) {
                    $mdToast.showSimple('Could not get requester modules.');
                }
            ).finally(function () {});
        }

        function getStatusName (status) {
            return status == 1 ? 'created' : (status == 2 ? 'in review' : (status == 3 ? 'in progress' : 'completed'));
        }
        function toggle(item) {
            var idx = self.selectedItems.indexOf(item);
            if (idx > -1) self.selectedItems.splice(idx, 1);
            else self.selectedItems.push(item);
        }
        function isSelected(item){
            return !(self.selectedItems.indexOf(item) < 0);
        }

        function sort(header){
            var sortedData = $filter('orderBy')(self.myModules, header, self.config.order==='descending');
            self.config.order = (self.config.order==='descending')?'ascending':'descending';
            self.config.order_by = header;
            self.myModules = sortedData;
        }

        function monitor(project) {
            window.location = 'monitor/' + project.id;
        }

        function createProject(){
            Project.clean();
            Project.create({create_milestone: true}).then(
                function success(response) {
                    var module_pk = response[0].id;
                    $location.path('/create-project/'+module_pk);
                },
                function error(response) {
                    $mdToast.showSimple('Could not get requester projects.');
                }
            ).finally(function () {});
        }

        function navigateToTasks(module_id){
            $location.path('/milestone-tasks/'+module_id);
        }

        function statusToString(status) {
            switch(status) {
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

        function resume(item) {
            Project.update(item.id, {status: 3}, 'module').then(
                function success(response) {
                    $mdToast.showSimple('Resumed ' + item.name + '!');
                    item.status = 3;
                },
                function error(response) {
                    $mdToast.showSimple('Could not resume module.');
                }
            ).finally(function () {});
        }

        function pause(item) {
            Project.update(item.id, {status: 5}, 'module').then(
                function success(response) {
                    $mdToast.showSimple('Paused ' + item.name + '!');
                    item.status = 5;
                },
                function error(response) {
                    $mdToast.showSimple('Could not pause module.');
                }
            ).finally(function () {});
        }

        function discard(item) {
            Project.deleteInstance(item.id).then(
                function success(response) {
                    self.myModules.splice(self.myModules.findIndex(function(element, index, array) {
                        return element.id == item.id;
                    }), 1)
                    $mdToast.showSimple('Deleted ' + item.name + '.');
                },
                function error(response) {
                    $mdToast.showSimple('Could not delete project.');
                }
            ).finally(function () {});
        }

        function edit(item) {
            $location.path('/create-project/' + item.id);
        }

        function fork(item) {
            Project.fork(item.id).then(
                function success(response) {
                    console.log(response[0]);
                    $location.path('/create-project/' + response[0].id);
                },
                function error(response) {
                    $mdToast.showSimple('Could not fork project.');
                }
            ).finally(function () {});
        }
    }
})();
