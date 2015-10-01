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
        self.myProjects = [];
        self.createProject = createProject;
        self.openProjectModules = openProjectModules;
        self.sort = sort;
        self.config = {
            order_by: "",
            order: ""
        };

        activate();
        function activate(){
            Project.getRequesterProjects().then(
                function success(response) {
                    self.myProjects = response[0];
                },
                function error(response) {
                    $mdToast.showSimple('Could not get requester projects.');
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

        function monitor(project) {
            window.location = 'monitor/' + project.id;
        }

        function createProject(){
            Project.clean();
            $location.path('/create-project/1');
        }

        function openProjectModules(project_id){
            $location.path('/milestones/'+project_id);
        }
    }
})();