(function () {
    'use strict';

    angular
        .module('crowdsource.project.controllers')
        .controller('ProjectController', ProjectController);

    ProjectController.$inject = ['$state', '$scope', '$mdToast', 'Project', '$stateParams',
        'Upload', 'helpersService', '$timeout', '$mdDialog'];

    /**
     * @namespace ProjectController
     */
    function ProjectController($state, $scope, $mdToast, Project, $stateParams, Upload, helpersService, $timeout, $mdDialog) {
        var self = this;
        self.save = save;
        self.deleteProject = deleteProject;
        self.publish = publish;
        self.removeFile = removeFile;
        self.project = {
            "pk": null
        };
        self.upload = upload;
        self.doPrototype = doPrototype;
        self.didPrototype = false;
        self.showPrototypeDialog = showPrototypeDialog;

        activate();
        function activate() {
            self.project.pk = $stateParams.projectId;
            Project.retrieve(self.project.pk, 'project').then(
                function success(response) {
                    self.project = response[0];
                },
                function error(response) {
                    $mdToast.showSimple('Could not get project.');
                }
            ).finally(function () {
            });
        }

        function doPrototype() {
            self.didPrototype = true;
        }


        function publish(e){
            var fieldsFilled = self.project.price && self.project.repetition>0
                                && self.project.templates[0].template_items.length;
            if(self.project.is_prototype && !self.didPrototype && fieldsFilled) {
                if(self.project.batch_files[0]) {
                    self.num_rows = self.project.batch_files[0].number_of_rows;
                } else {
                    self.num_rows = 1;
                }
                showPrototypeDialog(e);
            } else if(fieldsFilled){
                if(self.project.batch_files.length > 0) {
                    var num_rows = self.project.batch_files[0].number_of_rows;
                } else {
                    var num_rows = 0;
                }
                var request_data = {'status': 2, 'num_rows': num_rows};
                Project.update(self.project.id, request_data, 'project').then(
                    function success(response) {
                        $state.go('my_projects');
                    },
                    function error(response) {
                        $mdToast.showSimple('Could not update project status.');
                    }
                ).finally(function () {});
            } else {
                if(!self.project.price){
                    $mdToast.showSimple('Please enter task price ($/task).');
                }
                else if(!self.project.repetition){
                    $mdToast.showSimple('Please enter number of workers per task.');
                }
                else if(!self.project.templates[0].template_items.length){
                    $mdToast.showSimple('Please add at least one item to the template.');
                } else if(!self.didPrototype || self.num_rows) {
                    $mdToast.showSimple('Please enter the number of tasks');
                }
                return;
            }
        }
        var timeouts = {};
        var timeout;
        $scope.$watch('project.project', function (newValue, oldValue) {
            if (!angular.equals(newValue, oldValue) && self.project.id && oldValue.pk==undefined) {
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
		            Project.update(self.project.id, request_data, 'project').then(
                        function success(response) {

                        },
                        function error(response) {
                            $mdToast.showSimple('Could not update project data.');
                        }
                    ).finally(function () {
                    });
                }, 2048);
            }
        }, true);

        function save(){

        }


        function upload(files) {
            if (files && files.length) {
                for (var i = 0; i < files.length; i++) {
                    var file = files[i];
                    Upload.upload({
                        url: '/api/file/',
                        //fields: {'username': $scope.username},
                        file: file
                    }).progress(function (evt) {
                        var progressPercentage = parseInt(100.0 * evt.loaded / evt.total);
                        // console.log('progress: ' + progressPercentage + '% ' + evt.config.file.name);
                    }).success(function (data, status, headers, config) {
                        Project.attachFile(self.project.id, {"batch_file": data.id}).then(
                            function success(response) {
                                self.project.batch_files.push(data);
                            },
                            function error(response) {
                                $mdToast.showSimple('Could not upload file.');
                            }
                        ).finally(function () {
                        });

                    }).error(function (data, status, headers, config) {
                        $mdToast.showSimple('Error uploading spreadsheet.');
                    })
                }
            }
        }

        function deleteProject(){
            Project.deleteInstance(self.project.id).then(
                function success(response) {
                    $state.go('my_projects');
                },
                function error(response) {
                    $mdToast.showSimple('Could not delete project.');
                }
            ).finally(function () {
            });
        }

        function removeFile(pk){
            Project.deleteFile(self.project.id, {"batch_file": pk}).then(
                function success(response) {
                    self.project.batch_files = []; // TODO in case we have multiple splice
                },
                function error(response) {
                    $mdToast.showSimple('Could not remove file.');
                }
            ).finally(function () {
            });
        }

        function showPrototypeDialog($event) {
            var parent = angular.element(document.body);
            $mdDialog.show({
                clickOutsideToClose: true,
                scope: $scope,
                preserveScope: true,
                parent: parent,
                targetEvent: $event,
                templateUrl: '/static/templates/project/prototype.html',
                locals: {
                    project: self.project,
                    num_rows: self.num_rows
                },
                controller: DialogController
            });
            function DialogController($scope, $mdDialog) {
                $scope.hide = function() {
                    $mdDialog.hide();
                };
                $scope.cancel = function() {
                    $mdDialog.cancel();
                };
            }
        }
    }
})();
