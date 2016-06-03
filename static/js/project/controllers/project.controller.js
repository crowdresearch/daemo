(function () {
    'use strict';

    angular
        .module('crowdsource.project.controllers')
        .controller('ProjectController', ProjectController);

    ProjectController.$inject = ['$state', '$scope', '$mdToast', 'Project', '$stateParams',
        'Upload', '$timeout', '$mdDialog', 'User', '$filter'];

    /**
     * @namespace ProjectController
     */
    function ProjectController($state, $scope, $mdToast, Project, $stateParams, Upload, $timeout, $mdDialog, User,
                               $filter) {
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
        self.aws_account = null;
        self.create_or_update_aws = create_or_update_aws;
        self.showAWSDialog = showAWSDialog;
        self.AWSChanged = AWSChanged;
        self.createQualificationItem = createQualificationItem;
        self.deleteQualificationItem = deleteQualificationItem;
        self.updateQualificationItem = updateQualificationItem;
        self.transformChip = transformChip;
        self.qualificationItemAttribute = null;
        self.qualificationItemOperator = null;
        self.qualificationItemValue = null;
        self.openWorkerGroupNew = openWorkerGroupNew;
        self.workerGroups = [];
        self.workerGroup = {
            members: [],
            error: null,
            name: 'Untitled Group'
        };
        self.querySearch = querySearch;
        self.searchTextChange = searchTextChange;
        self.selectedItemChange = selectedItemChange;
        self.addWorkerGroup = addWorkerGroup;
        self.addWorkerGroupQualification = addWorkerGroupQualification;
        self.showNewItemForm = showNewItemForm;


        self.qualificationItemOptions = [
            {
                "name": "Approval Rate",
                "value": "approval_rate"
            },
            {
                "name": "Number of completed tasks",
                "value": "total_tasks"
            }/*,
             {
             "name": "Country",
             "value": "country"
             }*/
        ];

        self.qualificationOperatorMapping = {
            "approval_rate": [
                {
                    "name": "greater than",
                    "value": "gt"
                },
                {
                    "name": "less than",
                    "value": "lt"
                }
            ],
            "total_tasks": [
                {
                    "name": "greater than",
                    "value": "gt"
                },
                {
                    "name": "less than",
                    "value": "lt"
                }
            ]
            /*
             "country": [
             {
             "name": "in",
             "value": "in"
             },
             {
             "name": "not in",
             "value": "not_in"
             }
             ]*/
        };

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
                    getQualificationItems();
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

        function doPrototype() {
            self.didPrototype = true;
        }

        function publish(e) {
            var fieldsFilled = self.project.price && self.project.repetition > 0
                && self.project.template.items.length;
            if (self.project.is_prototype && !self.didPrototype && fieldsFilled) {
                if (self.project.batch_files[0]) {
                    self.num_rows = self.project.batch_files[0].number_of_rows;
                } else {
                    self.num_rows = 1;
                }
                showPrototypeDialog(e);
            } else if (fieldsFilled) {
                var num_rows = 0;
                if (self.project.batch_files.length > 0) {
                    num_rows = self.project.batch_files[0].number_of_rows;
                }
                var request_data = {'status': 2, 'num_rows': num_rows};
                Project.update(self.project.id, request_data, 'project').then(
                    function success(response) {
                        $state.go('my_projects');
                    },
                    function error(response) {
                        $mdToast.showSimple('Could not update project status.');
                    }
                ).finally(function () {
                });
            } else {
                if (!self.project.price) {
                    $mdToast.showSimple('Please enter task price ($/task).');
                }
                else if (!self.project.repetition) {
                    $mdToast.showSimple('Please enter number of workers per task.');
                }
                else if (!self.project.template.items.length) {
                    $mdToast.showSimple('Please add at least one item to the template.');
                } else if (!self.didPrototype || self.num_rows) {
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
                if (!angular.equals(newValue['qualification'], oldValue['qualification']) && newValue['qualification']) {
                    request_data['qualification'] = newValue['qualification'];
                    key = 'qualification';
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

                                // turn static sources to dynamic
                                if (self.project.template.items) {
                                    _.each(self.project.template.items, function (item) {
                                        // trigger watch to regenerate data sources
                                        item.force = !item.force;
                                    });
                                }
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
                    if (self.project.template.items) {
                        _.each(self.project.template.items, function (item) {
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
                controller: DialogController
            });
        }

        function DialogController($scope, $mdDialog) {
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

        function createQualification() {
            var data = {
                name: 'Project ' + self.project.pk + ' qualification'
            };
            Project.createQualification(data).then(
                function success(response) {
                    self.project.qualification = response[0].id;
                    createQualificationItem();
                },
                function error(response) {
                }
            ).finally(function () {
            });
        }

        function createQualificationItem() {
            if (self.project.qualification == null) {
                createQualification();
                return;
            }
            var data = {
                qualification: self.project.qualification,
                expression: {
                    "attribute": self.qualificationItemAttribute,
                    "operator": self.qualificationItemOperator,
                    "value": self.qualificationItemValue
                }
            };
            Project.createQualificationItem(data).then(
                function success(response) {
                    if (!self.project.hasOwnProperty('qualification_items')) {
                        angular.extend(self.project, {'qualification_items': []});
                    }
                    self.project.qualification_items.push(response[0]);
                    clearItem();

                },
                function error(response) {
                }
            ).finally(function () {
            });

        }

        function clearItem() {
            self.qualificationItemAttribute = null;
            self.qualificationItemOperator = null;
            self.qualificationItemValue = null;
        }

        function deleteQualificationItem(pk) {
            var item = $filter('filter')(self.project.qualification_items, {'id': pk})[0];
            self.project.qualification_items.splice(self.project.qualification_items.indexOf(item), 1);
            Project.deleteQualificationItem(pk).then(
                function success(response) {
                },
                function error(response) {
                }
            ).finally(function () {
            });
        }

        function updateQualificationItem(item) {
            Project.updateQualificationItem(item.id, item.expression).then(
                function success(response) {
                },
                function error(response) {
                }
            ).finally(function () {
            });
        }

        function getQualificationItems() {
            if (self.project.qualification && !self.project.qualification_items) {
                Project.getQualificationItems(self.project.qualification).then(
                    function success(response) {
                        if (!self.project.hasOwnProperty('qualification_items')) {
                            angular.extend(self.project, {'qualification_items': []});
                        }
                        self.project.qualification_items = response[0];
                        listFavoriteGroups();
                    },
                    function error(response) {
                    }
                ).finally(function () {
                });
            }
        }

        function openWorkerGroupNew($event) {
            var parent = angular.element(document.body);
            $mdDialog.show({
                clickOutsideToClose: true,
                scope: $scope,
                preserveScope: true,
                parent: parent,
                targetEvent: $event,
                templateUrl: '/static/templates/project/new-worker-group.html',
                controller: DialogController
            });
        }

        function transformChip(chip) {
            if (angular.isObject(chip)) {
                return chip;
            }
            return {name: chip, type: 'new'}
        }

        function querySearch(query) {
            return User.listUsernames(query).then(
                function success(data) {
                    return data[0];
                }
            );
        }

        function searchTextChange(text) {
        }

        function selectedItemChange(item) {
        }

        function addWorkerGroup() {
            if (self.workerGroup.members.length == 0) {
                self.workerGroup.error = 'You must select at least one worker.';
                return;
            }
            if (!self.workerGroup.name || self.workerGroup.name == '') {
                self.workerGroup.error = 'Enter a group name.';
                return;
            }
            var entries = [];
            angular.forEach(self.workerGroup.members, function (obj) {
                entries.push(obj.id);
            });
            var data = {
                name: self.workerGroup.name,
                type: 1,
                is_global: false,
                "entries": entries
            };

            User.createGroupWithMembers(data).then(
                function success(data) {
                    self.workerGroups.push(data[0]);
                    self.workerGroup.name = 'Untitled Group';
                    self.workerGroup.error = null;
                    self.workerGroup.members = [];
                    $scope.cancel();
                }
            );

        }

        function listFavoriteGroups() {
            User.listFavoriteGroups().then(
                function success(data) {
                    self.workerGroups = data[0];
                    setProjectWorkerGroup();
                }
            );
        }

        function setProjectWorkerGroup() {
            var item = filterWorkerGroupQualification();
            if (item.length) {
                self.project.workerGroup = parseInt(item[0].expression.value);
            }
            else {
                self.project.workerGroup = 0;
            }
        }

        function filterWorkerGroupQualification() {
            return $filter('filter')(self.project.qualification_items, function (value, index, array) {
                return value.expression.attribute == 'worker_groups';
            });
        }

        function addWorkerGroupQualification() {
            var existing = filterWorkerGroupQualification();
            if (!existing.length) {
                self.qualificationItemAttribute = 'worker_groups';
                self.qualificationItemOperator = 'contains';
                self.qualificationItemValue = self.project.workerGroup;
                if (parseInt(self.project.workerGroup) == 0) {
                    deleteQualificationItem(existing[0].id);
                }
                else {
                    createQualificationItem();
                }

            }
            else {
                if (parseInt(self.project.workerGroup) == 0) {
                    deleteQualificationItem(existing[0].id);
                }
                else {
                    existing[0].expression.value = self.project.workerGroup;
                    updateQualificationItem(existing[0]);
                }
            }

        }

        function showNewItemForm() {
            if (!self.project.qualification_items)
                return true;
            var workerQuals = filterWorkerGroupQualification();
            return (self.project.qualification_items.length - workerQuals.length) < self.qualificationItemOptions.length;
        }

    }
})();
