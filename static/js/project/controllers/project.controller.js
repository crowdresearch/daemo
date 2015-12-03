(function () {
    'use strict';

    angular
        .module('crowdsource.project.controllers')
        .controller('ProjectController', ProjectController);

    ProjectController.$inject = ['$location', '$scope', '$mdToast', 'Project', '$routeParams',
        'Upload', 'helpersService'];

    /**
     * @namespace ProjectController
     */
    function ProjectController($location, $scope, $mdToast, Project, $routeParams, Upload, helpersService) {
        var self = this;
        self.name = 'Untitled Project';
        self.milestone = {
            "repetition": 1,
            "price": null
        };
        self.upload = upload;
        self.currentProject = Project.retrieve();

        activate();
        function activate() {

        }


        function addMilestone() {
            var items = self.currentProject.template.items.map(function (item, index) {
                item.position = index;
                return item;
            });
        }

        $scope.$on("$destroy", function () {
            Project.syncLocally(self.currentProject);
        });

        function upload(files) {
            if (files && files.length) {
                for (var i = 0; i < files.length; i++) {
                    var file = files[i];
                    Upload.upload({
                        url: '/api/csvmanager/get-metadata-and-save',
                        fields: {'username': $scope.username},
                        file: file/*,
                         headers: {
                         'Authorization': tokens.token_type + ' ' + tokens.access_token
                         }*/
                    }).progress(function (evt) {
                        var progressPercentage = parseInt(100.0 * evt.loaded / evt.total);
                        console.log('progress: ' + progressPercentage + '% ' + evt.config.file.name);
                    }).success(function (data, status, headers, config) {
                        self.currentProject.metadata = data.metadata;

                        self.currentProject.metadata.column_headers = _.map(self.currentProject.metadata.column_headers, function (header) {
                            var text = "{" + header + "}";
                            return text;
                        });

                        if (self.currentProject.microFlag === 'micro') {
                            self.currentProject.totalTasks = self.currentProject.metadata.num_rows;
                        }
                        Project.syncLocally(self.currentProject);
                    }).error(function (data, status, headers, config) {
                        $mdToast.showSimple('Error uploading csv.');
                    })
                }
            }
        }
    }
})();
