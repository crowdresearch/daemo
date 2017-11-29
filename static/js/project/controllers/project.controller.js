(function () {
    'use strict';

    angular
        .module('crowdsource.project.controllers')
        .controller('ProjectController', ProjectController);

    ProjectController.$inject = ['$state', '$scope', '$mdToast', 'Project', '$stateParams',
        'Upload', '$timeout', '$mdDialog', 'User', '$filter', 'Task', '$location', '$window'];

    /**
     * @namespace ProjectController
     */
    function ProjectController($state, $scope, $mdToast, Project, $stateParams, Upload, $timeout, $mdDialog, User,
                               $filter, Task, $location, $window) {
        var self = this;
        // self.loading=true;
        self.deleteProject = deleteProject;
        self.validate = validate;
        self.removeFile = removeFile;
        self.isDisabled = isDisabled;
        self.upload = upload;
        self.showPrototypeDialog = showPrototypeDialog;
        self.minimumWageTime = 0;
        self.getMinWage = getMinWage;
        self.californiaMinWage = 10.5;
        self.selectedStep = 'design';
        self.insufficientFunds = null;
        self.financial_data = null;
        self.calculateTotalCost = totalCost;
        self.showPreview = false;
        self.templateHeight = templateHeight;
        self.calculatingTotal = false;
        self.fileUploading = false;
        self.selectedItem = null;
        self.amountToPay = 0;
        self.availableWorkerCount = 1;
        self.publishing = false;
        self.isLatestRevision = isLatestRevision;
        $scope.ctrlDown = false;
        $scope.ctrlKey = 17;
        $scope.cmdKey = 224;

        self.previewStyle = {
            // 'height': '450px'
        };
        self.project = {
            "pk": null
        };

        self.aws_account = null;

        self.create_or_update_aws = create_or_update_aws;
        self.showAWSDialog = showAWSDialog;
        self.AWSChanged = AWSChanged;
        self.createQualificationItem = createQualificationItem;
        self.deleteQualificationItem = deleteQualificationItem;
        self.updateQualificationItem = updateQualificationItem;
        self.transformChip = transformChip;
        self.createRevision = createRevision;
        self.qualificationItemAttribute = null;
        self.qualificationItemOperator = null;
        self.qualificationItemValue = null;
        self.openWorkerGroupNew = openWorkerGroupNew;
        self.showPublish = showPublish;
        self.showDataStep = false;
        self.goToData = goToData;
        self.setStep = setStep;
        self.goTo = goTo;
        self.saveMessage = '';
        self.workerGroups = [];
        self.submittedTasksCount = 0;
        self.workerGroup = {
            members: [],
            error: null,
            name: 'Untitled Group'
        };
        self.status = {
            STATUS_DRAFT: 1,
            STATUS_IN_PROGRESS: 3,
            STATUS_COMPLETED: 4,
            STATUS_PAUSED: 5
        };

        self.querySearch = querySearch;
        self.searchTextChange = searchTextChange;
        self.selectedItemChange = selectedItemChange;
        self.addWorkerGroup = addWorkerGroup;
        self.addWorkerGroupQualification = addWorkerGroupQualification;
        self.showNewItemForm = showNewItemForm;
        self.nextPage = nextPage;
        self.previousPage = previousPage;
        self.preview = preview;
        self.relaunchTask = relaunchTask;
        self.relaunchAll = relaunchAll;
        self.done = done;
        self.offset = 0;
        self.createRevisionInProgress = false;
        self.conflictsResolved = false;
        self.showInstructions = false;
        self.getStepNumber = getStepNumber;
        self.awsJustAdded = false;
        self.unlockText = '';
        self.unlockButtonText = 'Edit';
        self.resumeButtonText = 'Publish';
        self.showResume = showResume;
        self.isProfileCompleted = false;


        self.qualificationItemOptions = [
            /*{
             "name": "Approval Rate",
             "value": "approval_rate"
             },
             {
             "name": "Number of completed tasks",
             "value": "total_tasks"
             },
             {
             "name": "Location",
             "value": "location"
             }*/
            {
                "name": "Assignments completed by the worker",
                "value": "task_worker_id"
            }
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
            ],
            "task_worker_id": [
                {
                    "name": "is one of",
                    "value": "in"
                },
                {
                    "name": "is not one of",
                    "value": "not_in"
                }
            ]
        };

        self.project = {
            "pk": null
        };
        self.didPrototype = false;
        self.aws_account = null;

        function setStep(step, force) {
            if (!force) {
                if (!step.is_visited) return;
                self.selectedStep = step.key;
            }
            else {
                step.is_visited = true;
                self.selectedStep = step.key;
            }
        }

        $scope.publishAtMessages = {
            hour: 'Hour is required',
            minute: 'Minute is required',
            meridiem: 'Meridiem is required'
        };

        activate();

        function activate() {

            var today = new Date();
            self.minDate = new Date(today.getFullYear(), today.getMonth(), today.getDate());
            // $scope.time = {
            //     twelve: new Date(),
            //     twentyfour: new Date(),
            //     getMinutes: function () {
            //         return 12;
            //     },
            //     getHours: function () {
            //         return 0;
            //     }
            // };

            self.project.pk = $stateParams.projectId;

            // self.loading=true;
            Project.retrieve(self.project.pk, 'project').then(
                function success(response) {
                    self.project = response[0];

                    if (!self.project.publish_at) {
                        self.project.publish_at = new Date();
                    }
                    else {
                        self.project.publish_at = new Date(self.project.publish_at);
                    }
                    $scope.time = {
                        twelve: self.project.publish_at,
                        twentyfour: self.project.publish_at,
                        getHours: function () {
                            console.log(self.project.publish_at.getHours());
                            return self.project.publish_at.getHours();
                        },
                        getMinutes: function () {
                            return self.project.publish_at.getMinutes();
                        }
                    };


                    resetUnlockText();
                    if (self.project.deadline !== null) {
                        self.project.deadline = convertDate(self.project.deadline);
                    }
                    getQualificationItems();
                    if (!self.offset) {
                        self.offset = 0;
                    }
                    self.calculateTotalCost();
                    getSubmittedTasksCount();
                },
                function error(response) {
                    $mdToast.showSimple('Failed to retrieve project');
                }
            ).finally(function () {
                // self.loading=false;
                getAWS();
                getProfileCompletion();
                loadFinancialInfo();
                getAvailableWorkerCount();
            });

        }

        function getAvailableWorkerCount() {
            User.getAvailableWorkerCount().then(
                function success(response) {
                    self.availableWorkerCount = response[0].count;
                },
                function error(response) {

                }
            );
        }

        function loadFinancialInfo() {
            User.getFinancialData().then(
                function success(response) {
                    self.financial_data = response[0];
                },
                function error(response) {

                }
            );
        }

        function getProfileCompletion() {
            User.isProfileComplete().then(function success(response) {
                    self.isProfileCompleted = response[0].is_complete;
                },
                function error(response) {

                }
            );
        }

        function resetUnlockText() {
            if (self.project.status == self.status.STATUS_IN_PROGRESS) {
                self.unlockButtonText = 'Pause and Edit';
                self.unlockText = 'To pause and make it editable';
            }
            else if (self.project.status == self.status.STATUS_PAUSED) {
                self.unlockButtonText = 'Edit';
                self.unlockText = 'To make it editable';
                self.resumeButtonText = 'Resume';
            }
            else if (self.project.status == self.status.STATUS_DRAFT && self.project.revisions.length > 1) {
                self.resumeButtonText = 'Resume';
            }
        }

        function listTasks() {
            Task.list(self.project.id, self.offset).then(
                function success(response) {
                    if (response[0].tasks.length) {
                        self.project.headers = response[0].headers;
                        self.project.tasks = response[0].tasks;
                    }
                    else {
                        self.offset -= 10;
                    }

                },
                function error(response) {
                }
            ).finally(function () {
            });
        }

        function nextPage() {
            if (self.project.tasks.length < 10) {
                return;
            }
            self.offset += 10;
            listTasks();
        }

        function previousPage() {
            self.offset -= 10;
            if (self.offset < 0) {
                self.offset = 0;
            }
            listTasks();
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
            if (self.aws_account.client_secret === null || self.aws_account.client_id === null) {
                $mdToast.showSimple('Client key and secret are required');
            }
            User.create_or_update_aws(self.aws_account).then(
                function success(response) {
                    self.aws_account = response[0];
                    self.awsJustAdded = true;
                    self.AWSError = null;
                },
                function error(response) {
                    self.AWSError = 'Invalid keys or missing AmazonMechanicalTurkFullAccess policy, please try again.';
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


        function has_input_item(template_items) {
            var has_item = false;

            if (template_items) {
                var data_items = _.filter(template_items, function (item) {
                    if (item.role === 'input' || item.type === 'iframe') {
                        return true;
                    }
                });

                if (data_items.length > 0) {
                    has_item = true;
                }
            }

            return has_item;
        }

        function hasSrcValue(template_items) {
            var has_src = false;

            if (template_items) {
                var data_items = _.filter(template_items, function (item) {
                    if (item.type === 'image' || item.type === 'audio' || item.type === 'iframe') {
                        return true;
                    }
                });

                if (data_items.length > 0) {
                    var nullSources = _.filter(data_items, function (item) {
                        if (!item.aux_attributes.src || item.aux_attributes.src.trim() === "") {
                            return true;
                        }
                    });

                    return nullSources.length <= 0;
                }
            }

            return has_src;
        }

        function is_review_filled(has_review, review_price) {
            if (!has_review) {
                return true;
            }
            return review_price;
        }

        function validate(e) {
            var fieldsFilled = self.project.price
                && self.project.repetition > 0
                && self.project.template.items.length
                && has_input_item(self.project.template.items)
                //&& hasSrcValue(self.project.template.items)
                && is_review_filled(self.project.has_review, self.project.review_price)
            ;
            if (fieldsFilled) {
                return true;
            }
            else {
                if (!self.project.price) {
                    $mdToast.showSimple('Please enter task price ($/task).');
                }
                else if (!self.project.repetition) {
                    $mdToast.showSimple('Please enter number of workers per task.');
                }
                else if (!self.project.template.items.length) {
                    $mdToast.showSimple('Please add at least one item to the template.');
                }
                else if (!has_input_item(self.project.template.items)) {
                    $mdToast.showSimple('Please add at least one input item to the template.');
                }
                else if (!is_review_filled(self.project.has_review, self.project.review_price)) {
                    $mdToast.showSimple('Please enter task price for the review.');
                }
                return false;
            }
        }

        var timeouts = {};

        var timeout;

        $scope.$watch('project.project', function (newValue, oldValue) {
            if (self.project.status != self.status.STATUS_DRAFT)
                return;
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
                    self.calculatingTotal = true;
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
                if (!angular.equals(newValue['has_review'], oldValue['has_review']) && newValue['has_review'] != undefined) {
                    request_data['has_review'] = newValue['has_review'];
                    key = 'has_review';
                }
                if (!angular.equals(newValue['review_price'], oldValue['review_price']) && newValue['review_price']) {
                    request_data['review_price'] = newValue['review_price'];
                    key = 'review_price';
                }

                if (!angular.equals(newValue['task_price_field'], oldValue['task_price_field']) && newValue['task_price_field']) {
                    request_data['task_price_field'] = newValue['task_price_field'];
                    key = 'task_price_field';
                }

                if (!angular.equals(newValue['enable_boomerang'], oldValue['enable_boomerang'])
                    && (newValue['enable_boomerang'] === false || newValue['enable_boomerang'] === true)) {
                    request_data['enable_boomerang'] = newValue['enable_boomerang'];
                    key = 'enable_boomerang';
                }
                if (!angular.equals(newValue['allow_price_per_task'], oldValue['allow_price_per_task'])
                    && (newValue['allow_price_per_task'] === false || newValue['allow_price_per_task'] === true)) {
                    request_data['allow_price_per_task'] = newValue['allow_price_per_task'];
                    key = 'allow_price_per_task';
                }
                if (!angular.equals(newValue['publish_at'], oldValue['publish_at']) && newValue['publish_at']) {
                    request_data['publish_at'] = newValue['publish_at'];
                    key = 'publish_at';
                }
                if (key) {
                    self.saveMessage = 'Saving...';
                }
                if (angular.equals(request_data, {})) return;
                if ((key === 'allow_price_per_task' || key === 'task_price_field')
                    && self.project.batch_files.length) {
                    Project.update(self.project.id, request_data, 'project').then(
                        function success(response) {
                            Project.recreateTasks(self.project.id, {}).then(
                                function success(response) {
                                    self.saveMessage = 'All changes saved';
                                    self.calculateTotalCost();

                                }, function error(response) {
                                    $mdToast.showSimple('Could not recreate tasks.');
                                }
                            ).finally(function () {
                            });

                        },
                        function error(response) {
                            $mdToast.showSimple('Could not update project data.');
                        }
                    ).finally(function () {
                    });
                }
                else {
                    if (timeouts[key]) $timeout.cancel(timeouts[key]);
                    timeouts[key] = $timeout(function () {
                        Project.update(self.project.id, request_data, 'project').then(
                            function success(response) {
                                self.saveMessage = 'All changes saved';
                                self.calculateTotalCost();

                            },
                            function error(response) {
                                $mdToast.showSimple('Could not update project data.');
                            }
                        ).finally(function () {
                        });
                    }, 512);
                }

            }
        }, true);

        $scope.$on('profileUpdated',
            function (event, data) {
                if (data.is_valid) {
                    self.isProfileCompleted = true;
                }
            }
        );

        function upload(files) {
            if (files && files.length) {
                self.calculatingTotal = true;
                self.fileUploading = true;
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
                                self.fileUploading = false;
                                //self.calculatingTotal = false;
                                $timeout(function () {
                                    self.calculateTotalCost();
                                }, 10);
                                get_relaunch_info();
                                // turn static sources to dynamic
                                if (self.project.template.items) {
                                    _.each(self.project.template.items, function (item) {
                                        // trigger watch to regenerate data sources
                                        item.force = !item.force;
                                    });
                                }
                            },
                            function error(response) {
                                self.calculatingTotal = false;
                                self.fileUploading = false;
                                $mdToast.showSimple('Could not upload file.');
                            }
                        );
                    }).error(function (data, status, headers, config) {
                        self.calculatingTotal = false;
                        self.fileUploading = false;
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

        function getSubmittedTasksCount() {
            Project.retrieveSubmittedTasksCount(self.project.id).then(
                function success(response) {
                    self.submittedTasksCount = response[0].submitted;
                },
                function error(response) {
                }
            ).finally(function () {
            });
        }

        function removeFile(pk) {
            self.calculatingTotal = true;
            Project.deleteFile(self.project.id, {"batch_file": pk}).then(
                function success(response) {
                    self.project.batch_files = []; // TODO in case we have multiple splice
                    get_relaunch_info();
                    $timeout(function () {
                        self.calculateTotalCost();
                    }, 1000);
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
                    self.calculatingTotal = false;
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
                        'num_rows': $scope.num_rows,
                        'repetition': $scope.project.repetition
                    };

                    Project.publish(project.id, request_data).then(
                        function success(response) {
                            dialog.hide();
                            $state.go('my_projects');
                        },
                        function error(response) {

                            if (response[1] == 402) {
                                self.project.insufficientFunds = "You don't have enough funds to publish this project";
                            }

                            if (Array.isArray(response[0])) {
                                _.forEach(response[0], function (error) {
                                    $mdToast.showSimple(error);
                                });

                                if (response[0].hasOwnProperty('non_field_errors')) {
                                    _.forEach(response[0].non_field_errors, function (error) {
                                        $mdToast.showSimple(error);
                                    });
                                }
                            }

                        }
                    );
                }
            }
        }

        function getMinWage() {
            if (!self.project.price) {
                return '0 seconds'
            }
            else {
                var p = self.project.price / self.californiaMinWage;
                if (p > 0.017) {
                    return Math.round((p * 60)).toString() === '1' ? '1 minute' : Math.round((p * 60)).toString() + ' minutes';
                }
                return Math.round((p * 60) * 60).toString() + ' seconds';
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
            if (self.project.qualification === null) {
                createQualification();
                return;
            }
            var data = {
                qualification: self.project.qualification,
                expression: {
                    "attribute": self.qualificationItemAttribute,
                    "operator": self.qualificationItemOperator,
                    "value": self.qualificationItemValue
                },
                scope: self.qualificationItemAttribute === 'task_worker_id' ? 'task' : 'project'
            };
            if (data.expression.attribute === 'location') {
                data.expression.value = data.expression.value.replace(' ', '').split(',');
            }
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
            if (item.expression.attribute == 'location') {
                item.expression.value = item.expression.value.replace(' ', '').split(',');
            }
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
            else {
                listFavoriteGroups();
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
            if (item && item.length) {
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

            if (!existing || !existing.length) {
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

        function isDisabled() {
            return self.project.status != self.status.STATUS_DRAFT;
        }


        function createRevision() {
            self.createRevisionInProgress = true;
            Project.createRevision(self.project.id).then(
                function success(response) {
                    var project_pk = response[0].id;
                    $state.go('create_edit_project', {projectId: project_pk});
                },
                function error(response) {
                    self.createRevisionInProgress = false;
                }
            ).finally(function () {
            });
        }

        function relaunchTask(task) {
            task.exclude = true;
            Task.relaunch(task.id).then(
                function success(response) {
                    self.conflictsResolved =
                        $filter('filter')(self.project.tasks, {'exclude': true}).length == self.project.tasks.length;
                },
                function error(response) {
                }
            ).finally(function () {
            });
        }

        function showPublish() {
            if (!self.project.id || self.project.status != self.status.STATUS_DRAFT || self.project.is_api_only)
                return false;
            return self.project.status == self.status.STATUS_DRAFT &&
                ((self.project.id == self.project.group_id || self.showDataStep) ||
                    (self.project.relaunch.is_forced || (!self.project.relaunch.is_forced
                        && !self.project.relaunch.ask_for_relaunch)));
        }

        function goToData() {
            self.showDataStep = true;
            listTasks();
        }

        function goTo(state) {
            var params = {
                suggestedAmount: self.amountToPay - self.financial_data.account_balance,
                redirectTo: $location.url()
            };
            $state.go(state, params);
        }

        function get_relaunch_info() {
            Project.get_relaunch_info(self.project.id).then(
                function success(response) {
                    self.project.relaunch = response[0].relaunch;
                },
                function error(response) {
                }
            ).finally(function () {
            });
        }

        function relaunchAll() {
            Task.relaunchAll(self.project.id).then(
                function success(response) {
                    self.conflictsResolved = true;
                },
                function error(response) {
                }
            ).finally(function () {
            });
        }

        function done($event) {
            // if (self.project.post_mturk && !self.aws_account.id) {
            //     showAWSDialog($event);
            //     return;
            // }
            if (!validate($event)) return;

            self.publishing = true;
            var publishText = self.resumeButtonText;
            self.resumeButtonText = 'Publishing...';
            Project.publish(self.project.id, {status: self.status.STATUS_IN_PROGRESS}).then(
                function success(response) {
                    self.publishing = false;
                    $state.go('my_projects');
                },
                function error(response) {
                    self.resumeButtonText = 'Publish';
                    self.publishing = false;
                    User.getFinancialData().then(
                        function success(response) {
                            self.financial_data = response[0];
                        },
                        function error(response) {

                        }
                    );
                    if (response[1] == 402) {
                        self.insufficientFunds = "You don't have enough funds to publish this project";
                        $mdToast.showSimple(self.insufficientFunds);
                        return;
                    }

                    if (Array.isArray(response[0])) {
                        _.forEach(response[0], function (error) {
                            $mdToast.showSimple(error);
                        });

                        if (response[0].hasOwnProperty('non_field_errors')) {
                            _.forEach(response[0].non_field_errors, function (error) {
                                $mdToast.showSimple(error);
                            });
                        }
                    }
                }
            ).finally(function () {
            });

            //}
        }

        function getStepNumber(id) {
            if (self.aws_account && self.aws_account.id && !self.awsJustAdded) return id - 1;
            return id;
        }

        function showResume() {
            return (self.project.status === self.status.STATUS_PAUSED || self.project.status === self.status.STATUS_DRAFT) && isLatestRevision();
        }

        function totalCost() {
            if (!self.project || !self.project.batch_files) return 0;
            Project.retrievePaymentInfo(self.project.id).then(
                function success(data) {
                    self.amountToPay = data[0].to_pay;
                    self.calculatingTotal = false;
                },
                function error(errData) {
                    self.calculatingTotal = false;

                }
            ).finally(function () {
            });
        }

        function preview(event) {
            $window.open('task-feed/' + self.project.id, '_blank');
        }

        function templateHeight() {
            var template_height = angular.element('._template-builder').height();
            return template_height - template_height / 3 + 'px';
        }

        /*
        // not working on Chrome sometimes
        angular.element($window).bind("keyup", function ($event) {
            if ($event.keyCode === $scope.ctrlKey || $event.keyCode === $scope.cmdKey ||
                $event.keyCode === 91 || $event.keyCode === 93)
                $scope.ctrlDown = false;

            $scope.$apply();
        });

        angular.element($window).bind("keydown", function ($event) {
            if ($event.keyCode === $scope.ctrlKey || $event.keyCode === $scope.cmdKey
                || $event.keyCode === 91 || $event.keyCode === 93)
                $scope.ctrlDown = true;
            if ($scope.ctrlDown && String.fromCharCode($event.which).toLowerCase() === 's') {
                $event.preventDefault();

            }
            $scope.$apply();
        });
        */

        function isLatestRevision() {
            var isLatest = true;
            if (!self.project || !self.project.revisions) {
                return false;
            }
            for (var i = 0; i < self.project.revisions.length; i++) {
                if (self.project.revisions[i] > self.project.id) {
                    isLatest = false;
                }
            }
            return isLatest;
        }
    }
})();
