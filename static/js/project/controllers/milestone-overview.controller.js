(function () {
    'use strict';

    angular
        .module('crowdsource.project.controllers')
        .controller('MilestoneOverviewController', MilestoneOverviewController);

    MilestoneOverviewController.$inject = ['$window', '$location', '$scope', '$mdToast', 'Project',
        '$filter', '$routeParams', 'Authentication'];

    /**
     * @namespace MilestoneOverviewController
     */
    function MilestoneOverviewController($window, $location, $scope, $mdToast, Project,
                               $filter, $routeParams, Authentication) {
        var self = this;
        self.modules = [];
        self.createMilestone = createMilestone;
        self.getStatusName = getStatusName;
        self.navigateToTasks = navigateToTasks;
        self.navigateToMyProjects = navigateToMyProjects;
        self.sort = sort;
        self.config = {
            order_by: "",
            order: ""
        };

        activate();
        function activate(){
            var project_id = $routeParams.projectId;
            Project.getModules(project_id).then(
                function success(response) {
                    self.modules = response[0].modules;
                    self.project_name = response[0].project_name;
                },
                function error(response) {
                    $mdToast.showSimple('Could not get modules.');
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
            var sortedData = $filter('orderBy')(self.myProjects, header, self.config.order==='descending');
            self.config.order = (self.config.order==='descending')?'ascending':'descending';
            self.config.order_by = header;
            self.myProjects = sortedData;
        }

        function createMilestone(){
            var project_id = $routeParams.projectId;
            $location.path('/add-milestone/'+project_id+'/1');
        }

        function navigateToTasks(module_id){
            $location.path('/milestone-tasks/'+module_id);
        }

        function navigateToMyProjects() {
            $location.path('/my-projects');
        }
    }
})();