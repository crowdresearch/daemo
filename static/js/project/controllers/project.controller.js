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
        self.pk = null;
        self.name = null;
        self.save = save;
        self.module = {
            "pk": null
        };
        self.upload = upload;

        activate();
        function activate() {
            self.module.pk = $routeParams.moduleId;
            Project.retrieve(self.module.pk, 'module').then(
                function success(response) {
                    var response_data = response[0];
                    self.name = response_data.project.name;
                    self.pk = response_data.project.id;
                    delete response_data['project'];
                    Project.currentModule = response_data;
                    self.module = Project.currentModule;
                },
                function error(response) {
                    $mdToast.showSimple('Could not get project.');
                }
            ).finally(function () {
            });
        }

        $scope.$watch('project.name', function (newValue, oldValue) {
            if (!angular.equals(newValue, oldValue) && self.pk && oldValue) {
                Project.update(self.pk, {name: newValue}, 'project').then(
                    function success(response) {

                    },
                    function error(response) {
                        $mdToast.showSimple('Could not update project name.');
                    }
                ).finally(function () {
                });
            }
        });
        $scope.$watch('project.module', function (newValue, oldValue) {
            if (!angular.equals(newValue, oldValue) && self.module.id && oldValue.pk==undefined) {
                var request_data = {};
                if(!angular.equals(newValue['price'], oldValue['price'])){
                    request_data['price'] = newValue['price'];
                }
                if(!angular.equals(newValue['repetition'], oldValue['repetition'])){
                    request_data['repetition'] = newValue['repetition'];
                }
                if (angular.equals(request_data, {})) return;
                Project.update(self.module.id, request_data, 'module').then(
                    function success(response) {

                    },
                    function error(response) {
                        $mdToast.showSimple('Could not update module data.');
                    }
                ).finally(function () {
                });
            }
        }, true);

        function save(){

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
