(function () {
    'use strict';

    angular
        .module('crowdsource.project.controllers')
        .controller('ProjectController', ProjectController);

    ProjectController.$inject = ['$state', '$scope', '$mdToast', 'Project', '$stateParams',
        'Upload', '$timeout', '$mdDialog', 'User'];

    /**
     * @namespace ProjectController
     */
    function ProjectController($state, $scope, $mdToast, Project, $stateParams, Upload, $timeout, $mdDialog, User) {
        var self = this;
        self.deleteProject = deleteProject;
        self.validate = validate;
        self.removeFile = removeFile;
        self.upload = upload;
        self.showPrototypeDialog = showPrototypeDialog;

        self.project = {
            "pk": null
        };

        self.aws_account = null;
        self.create_or_update_aws = create_or_update_aws;
        self.showAWSDialog = showAWSDialog;
        self.AWSChanged = AWSChanged;

        activate();

        function activate() {
            var today = new Date();
            self.minDate = new Date(today.getFullYear(), today.getMonth(), today.getDate());

            self.project.pk = $stateParams.projectId;

            Project.retrieve(self.project.pk, 'project').then(
                function success(response) {
                    self.project = response[0];

                    if (self.project.deadline == null) {
                        //self.project.deadline = self.minDate;
                    } else {
                        self.project.deadline = convertDate(self.project.deadline);
                    }
                },
                function error(response) {
                    $mdToast.showSimple('Could not get project.');
                }
            ).finally(function () {
                    getAWS();
                });
        }

        function getAWS() {
            User.get_aws_account().then(
                function success(response) {
                    self.aws_account = response[0];
                    self.project.post_mturk = !!self.aws_account;
                },
                function error(response) {

                }
            ).finally(function () {

                });
        }

        function create_or_update_aws() {
            if (self.aws_account.client_secret == null || self.aws_account.client_id == null) {
                $mdToast.showSimple('Client key and secret are required');
            }
            User.create_or_update_aws(self.aws_account).then(
                function success(response) {
                    self.aws_account = response[0];
                    self.AWSError = null;
                },
                function error(response) {
                    self.AWSError = 'Invalid keys, please try again.';
                    self.project.post_mturk = false;
                }
            ).finally(function () {

                });
        }


        function convertDate(value) {
            var regexIso8601 = /^([\+-]?\d{4}(?!\d{2}\b))((-?)((0[1-9]|1[0-2])(\3([12]\d|0[1-9]|3[01]))?|W([0-4]\d|5[0-2])(-?[1-7])?|(00[1-9]|0[1-9]\d|[12]\d{2}|3([0-5]\d|6[1-6])))([T\s]((([01]\d|2[0-3])((:?)[0-5]\d)?|24\:?00)([\.,]\d+(?!:))?)?(\17[0-5]\d([\.,]\d+)?)?([zZ]|([\+-])([01]\d|2[0-3]):?([0-5]\d)?)?)?)?$/;
            var match;
            if (typeof value === "string" && (match = value.match(regexIso8601))) {
                // Assume that Date.parse can parse ISO 8601 strings, or has been shimmed in older browsers to do so.
                var milliseconds = Date.parse(match[0]);
                if (!isNaN(milliseconds)) {
                    return new Date(milliseconds);
                }
            } else {
                return self.minDate;
            }
        }

        function check_csv_linkage(template_items) {
            var is_linked = false;

            if (template_items) {
                var data_items = _.find(template_items, function (item) {
                    if (item.aux_attributes.question.data_source != null) {

                        var dynamicSources = _.find(item.aux_attributes.question.data_source, function (source) {
                            return source.type == "dynamic";
                        });

                        if (dynamicSources != null) {
                            return true;
                        }
                    }

                    if (item.aux_attributes.hasOwnProperty('options') && item.aux_attributes.options) {
                        var dynamicOptions = _.find(item.aux_attributes.options, function (option) {
                            if (option.data_source != null) {
                                var dynamicSources = _.find(option.data_source, function (source) {
                                    return source.type == "dynamic";
                                });

                                if (dynamicSources != null) {
                                    return true;
                                }
                            }
                        });

                        if (dynamicOptions != null) {
                            return true;
                        }
                    }

                    return false;
                });

                if (data_items!=null) {
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
                    && has_input_item(self.project.templates[0].template_items)
                ;

            if (fieldsFilled) {
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
                else if (!self.num_rows) {
                    $mdToast.showSimple('Please enter the number of tasks');
                }
            }
        }

        var timeouts = {};

        var timeout;

        $scope.$watch('project.project', function (newValue, oldValue) {
            if (!angular.equals(newValue, oldValue) && self.project.id) {
                var request_data = {};
                var key = null;
                if (!angular.equals(newValue['name'], oldValue['name']) && newValue['name']) {
                    request_data['name'] = newValue['name'];
                    key = 'name';
                }
                if (!angular.equals(newValue['post_mturk'], oldValue['post_mturk']) && newValue['post_mturk']) {
                    request_data['post_mturk'] = newValue['post_mturk'];
                    key = 'post_mturk';
                }
                if (!angular.equals(newValue['price'], oldValue['price']) && newValue['price']) {
                    request_data['price'] = newValue['price'];
                    key = 'price';
                }

                if (!angular.equals(newValue['repetition'], oldValue['repetition']) && newValue['repetition']) {
                    request_data['repetition'] = newValue['repetition'];
                    key = 'repetition';
                }
                if (!angular.equals(newValue['deadline'], oldValue['deadline']) && newValue['deadline']) {
                    request_data['deadline'] = newValue['deadline'];
                    key = 'deadline';
                }
                if (!angular.equals(newValue['timeout'], oldValue['timeout']) && newValue['timeout']) {
                    request_data['timeout'] = newValue['timeout'];
                    key = 'timeout';
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

                                // turn static sources to dynamic
                                if (self.project.templates[0].template_items) {
                                    _.each(self.project.templates[0].template_items, function (item) {
                                        // trigger watch to regenerate data sources
                                        item.force = !item.force;
                                    });
                                }
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
                    $state.go('my_projects');
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

                    // turn dynamic sources to static
                    if (self.project.templates[0].template_items) {
                        _.each(self.project.templates[0].template_items, function (item) {
                            // trigger watch to regenerate data sources
                            item.force = !item.force;
                        });
                    }
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
                            $state.go('my_projects');
                        },
                        function error(response) {
                            _.forEach(response[0], function (error) {
                                $mdToast.showSimple(error);
                            });

                            if (response[0].hasOwnProperty('non_field_errors')) {
                                _.forEach(response[0].non_field_errors, function (error) {
                                    $mdToast.showSimple(error);
                                });
                            }

                        }
                    );
                }
            }
        }

        function showAWSDialog($event) {
            var parent = angular.element(document.body);
            $mdDialog.show({
                clickOutsideToClose: true,
                scope: $scope,
                preserveScope: true,
                parent: parent,
                targetEvent: $event,
                templateUrl: '/static/templates/project/add-aws.html',
                controller: AWSDialogController
            });
        }

        function AWSDialogController($scope, $mdDialog) {
            $scope.hide = function () {
                $mdDialog.hide();
            };
            $scope.cancel = function () {
                $mdDialog.cancel();
            };
        }

        function AWSChanged($event) {
            if (self.project.post_mturk && !self.aws_account.id)
                showAWSDialog($event);
        }
    }
})();
