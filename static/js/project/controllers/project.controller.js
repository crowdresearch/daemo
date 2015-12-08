(function () {
    'use strict';

    angular
        .module('crowdsource.project.controllers')
        .controller('ProjectController', ProjectController);

    ProjectController.$inject = ['$location', '$scope', '$mdToast', 'Project', '$routeParams',
        'Upload', 'helpersService', '$timeout'];

    /**
     * @namespace ProjectController
     */
    function ProjectController($location, $scope, $mdToast, Project, $routeParams, Upload, helpersService, $timeout) {
        var self = this;
        self.save = save;
        self.deleteModule = deleteModule;
        self.publish = publish;
        self.module = {
            "pk": null
        };
        self.upload = upload;

        activate();
        function activate() {
            self.module.pk = $routeParams.moduleId;
            Project.retrieve(self.module.pk, 'module').then(
                function success(response) {
                    self.module = response[0];
                },
                function error(response) {
                    $mdToast.showSimple('Could not get project.');
                }
            ).finally(function () {
            });
        }
        function publish(){
            if(self.module.price && self.module.repetition>0 && self.module.templates[0].template_items.length){
                Project.update(self.module.id, {'status': 3}, 'module').then(
                    function success(response) {
                        self.module.status = 3;
                        $location.path('/my-projects');
                    },
                    function error(response) {
                        $mdToast.showSimple('Could not update module status.');
                    }
                ).finally(function () {
                });
            }
        }
        var timeouts = {};
        var timeout;
        $scope.$watch('project.module', function (newValue, oldValue) {
            if (!angular.equals(newValue, oldValue) && self.module.id && oldValue.pk==undefined) {
                var request_data = {};
                var key = null;
                if(!angular.equals(newValue['name'], oldValue['name']) && newValue['name']){
                    request_data['name'] = newValue['name'];
                    key = 'name';
                }
                if(!angular.equals(newValue['price'], oldValue['price']) && newValue['price']){
                    request_data['price'] = newValue['price'];
                    key = 'price';
                }
                if(!angular.equals(newValue['repetition'], oldValue['repetition']) && oldValue['repetition']){
                    request_data['repetition'] = newValue['repetition'];
                    key = 'repetition';
                }
                if (angular.equals(request_data, {})) return;
                if(timeouts[key]) $timeout.cancel(timeouts[key]);
                timeouts[key] = $timeout(function() {
		            Project.update(self.module.id, request_data, 'module').then(
                        function success(response) {

                        },
                        function error(response) {
                            $mdToast.showSimple('Could not update module data.');
                        }
                    ).finally(function () {
                    });
                }, 2048);
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

        function deleteModule(){
            Project.deleteInstance(self.module.id).then(
                function success(response) {
                    $location.path('/my-projects');
                },
                function error(response) {
                    $mdToast.showSimple('Could not delete project.');
                }
            ).finally(function () {
            });
        }


    }
})();
