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
                    return "Saved";
                case 3:
                    return "Published";
                case 4:
                    return "Completed";
                case 5:
                    return "Paused";
                default:
                    return "Draft";
            }
        }
    }
})();
