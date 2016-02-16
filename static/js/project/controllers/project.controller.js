(function () {
    'use strict';

    angular
        .module('crowdsource.project.controllers')
        .controller('ProjectController', ProjectController);

    ProjectController.$inject = ['$location', '$scope', '$mdToast', 'Project', '$routeParams',
        'Upload', 'helpersService', '$timeout', '$mdDialog'];

    /**
     * @namespace ProjectController
     */
    function ProjectController($location, $scope, $mdToast, Project, $routeParams, Upload, helpersService, $timeout, $mdDialog) {
        var self = this;
        self.save = save;
        self.deleteProject = deleteProject;
        self.validate = validate;
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
            self.project.pk = $routeParams.projectId;
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


        function check_csv_linkage(template_items) {
            var is_linked = false;

            if (template_items) {
                var data_items = _.filter(template_items, function (item) {
                    if (item.aux_attributes.question.data_source != null) {
                        return true;
                    }

                    if (item.aux_attributes.hasOwnProperty('options') && item.aux_attributes.options) {
                        var data_options = _.filter(item.aux_attributes.options, function (option) {
                            if (option.data_source != null) {
                                return true;
                            }
                        });

                        if (data_options.length > 0) {
                            return true;
                        }
                    }

                    return false;
                });

                if (data_items.length > 0) {
                    is_linked = true;
                }
            }

            return is_linked;
        }

        function has_input_item(template_items) {
            var has_item = false;

            if (template_items) {
                var data_items = _.filter(template_items, function (item) {
                    if (item.role == 'input' || item.type == 'iframe') {
                        return true;
                    }
                });

                if (data_items.length > 0) {
                    has_item = true;
                }
            }

            return has_item;
        }

        function validate(e) {
            var fieldsFilled = self.project.price
                && self.project.repetition > 0
                && self.project.templates[0].template_items.length
                && has_input_item(self.project.templates[0].template_items);

            if (self.project.is_prototype && !self.didPrototype && fieldsFilled) {
                self.num_rows = 1;

                if (self.project.batch_files[0]) {
                    if (check_csv_linkage(self.project.templates[0].template_items)) {
                        self.num_rows = self.project.batch_files[0].number_of_rows;
                    }
                }

                showPrototypeDialog(e, self.project, self.num_rows);

            } else {
                if (!self.project.price) {
                    $mdToast.showSimple('Please enter task price ($/task).');
                }
                else if (!self.project.repetition) {
                    $mdToast.showSimple('Please enter number of workers per task.');
                }
                else if (!self.project.templates[0].template_items.length) {
                    $mdToast.showSimple('Please add at least one item to the template.');
                }
                else if (!has_input_item(self.project.templates[0].template_items)) {
                    $mdToast.showSimple('Please add at least one input item to the template.');
                }
                else if (!self.didPrototype || self.num_rows) {
                    $mdToast.showSimple('Please enter the number of tasks');
                }
            }
        }

        var timeouts = {};

        var timeout;

        $scope.$watch('project.project', function (newValue, oldValue) {
            if (!angular.equals(newValue, oldValue) && self.project.id && oldValue.pk == undefined) {
                var request_data = {};
                var key = null;
                if (!angular.equals(newValue['name'], oldValue['name']) && newValue['name']) {
                    request_data['name'] = newValue['name'];
                    key = 'name';
                }
                if (!angular.equals(newValue['price'], oldValue['price']) && newValue['price']) {
                    request_data['price'] = newValue['price'];
                    key = 'price';
                }
                if (!angular.equals(newValue['repetition'], oldValue['repetition']) && oldValue['repetition']) {
                    request_data['repetition'] = newValue['repetition'];
                    key = 'repetition';
                }
                if (angular.equals(request_data, {})) return;
                if (timeouts[key]) $timeout.cancel(timeouts[key]);
                timeouts[key] = $timeout(function () {
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

        function save() {

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
                        );

                    }).error(function (data, status, headers, config) {
                        $mdToast.showSimple('Error uploading spreadsheet.');
                    })
                }
            }
        }

        function deleteProject() {
            Project.deleteInstance(self.project.id).then(
                function success(response) {
                    $location.path('/my-projects');
                },
                function error(response) {
                    $mdToast.showSimple('Could not delete project.');
                }
            ).finally(function () {
                });
        }

        function removeFile(pk) {
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

        function showPrototypeDialog($event, project, rows) {
            $mdDialog.show({
                clickOutsideToClose: true,
                preserveScope: false,
                targetEvent: $event,
                templateUrl: '/static/templates/project/prototype.html',
                locals: {
                    dialog: $mdDialog,
                    project: project,
                    rows: rows
                },
                controller: DialogController
            });

            function DialogController($scope, dialog, project, rows) {
                $scope.max_rows = rows || 1;
                $scope.num_rows = rows || 1;
                $scope.project = project;

                $scope.hide = function () {
                    dialog.hide();
                };
                $scope.cancel = function () {
                    dialog.cancel();
                };

                $scope.publish = function () {
                    var request_data = {
                        'status': 2,
                        'num_rows': $scope.num_rows,
                        'repetition': $scope.project.repetition
                    };

                    Project.update(project.id, request_data, 'project').then(
                        function success(response) {
                            dialog.hide();
                            $location.path('/my-projects');
                        },
                        function error(response) {
                            _.forEach(response[0], function(error){
                                $mdToast.showSimple(error);
                            });

                        }
                    );
                }
            }

        }
    }
})();
