/**
 * ProjectController
 * @namespace crowdsource.project.controllers
 * @author dmorina neilthemathguy
 */
(function () {
    'use strict';

    angular
        .module('crowdsource.project.controllers')
        .controller('ProjectController', ProjectController);

    ProjectController.$inject = ['$window', '$location', '$scope', 'Project', '$filter', '$mdSidenav', '$routeParams', 'Skill'];

    /**
     * @namespace ProjectController
     */
    function ProjectController($window, $location, $scope, Project, $filter, $mdSidenav, $routeParams) {
        var self = this;
        self.addProject = addProject;
        self.startDate = $filter('date')(new Date(), 'yyyy-MM-ddTHH:mmZ');
        self.endDate = $filter('date')(new Date(), 'yyyy-MM-ddTHH:mmZ');
        self.getReferenceData = getReferenceData;
        self.categories = [];
        self.getSelectedCategories = getSelectedCategories;
        self.showTemplates = showTemplates;
        self.closeSideNav = closeSideNav;
        self.finishModules = finishModules;
        self.activateTemplate = activateTemplate;
        self.addTemplate = addTemplate;
        self.addModule = addModule;
        self.currentProject = getProject();
        self.selectedItems = [];
        self.isSelected = isSelected;
        self.sort = sort;
        self.config = {
            order_by: "",
            order: ""
        };

        self.wizard = {
            steps: [
                {
                    id: 1, key: "category", name: "Category",
                    is_dirty: false, is_valid: false,
                    validate: function () {
                        return (self.currentProject.selectedCategory != null);
                    }
                },
                {
                    id: 2, key: "general_info", name: "Description",
                    is_dirty: false, is_valid: false,
                    validate: function () {
                        self.currentProject.name = self.currentProject.name || "";
                        $scope.projectForm.name.$touched = true;

                        self.currentProject.description = self.currentProject.description || "";
                        $scope.projectForm.description.$touched = true;

                        return self.currentProject.name.length > 1 && self.currentProject.description.length > 1;
                    }
                },
                {
                    id: 3, key: "modules", name: "Prototype Task",
                    is_dirty: false, is_valid: false,
                    validate: function () {
                        self.currentProject.milestoneDescription = self.currentProject.milestoneDescription || "";
                        $scope.projectForm.milestoneDescription.$touched = true;

                        $scope.projectForm.upload.$touched = true;

                        self.currentProject.onetaskTime = self.currentProject.onetaskTime || null;
                        $scope.projectForm.onetaskTime.$touched = true;

                        self.currentProject.numberofTasks = self.currentProject.numberofTasks || 1;
                        $scope.projectForm.numberofTasks.$touched = true;

                        if (self.currentProject.upload == "google" || self.currentProject.upload == "myWebPage") {
                            self.currentProject.url = self.currentProject.url || null;
                            if (self.currentProject.url == "") {
                                self.currentProject.url = null;
                            }
                        } else {
                            self.currentProject.url = self.currentProject.url || "";
                        }

                        $scope.projectForm.url.$touched = true;

                        return self.currentProject.milestoneDescription.length > 1 && self.currentProject.upload && self.currentProject.onetaskTime && self.currentProject.numberofTasks && self.currentProject.url != null;
                    }
                },
                {
                    id: 4, key: "templates", name: "Design",
                    is_dirty: false, is_valid: false,
                    validate: function () {
                        return true;
                    }
                },
                {
                    id: 5, key: "payment", name: "Payment",
                    is_dirty: false, is_valid: false,
                    validate: function () {
                        self.currentProject.payment.number_of_hits = self.currentProject.payment.number_of_hits || null;
                        $scope.projectForm.number_of_hits.$touched = true;

                        self.currentProject.payment.wage_per_hit = self.currentProject.payment.wage_per_hit || null;
                        $scope.projectForm.wage_per_hit.$touched = true;

                        self.currentProject.payment.charges = self.currentProject.payment.charges || null;
                        $scope.projectForm.charges.$touched = true;

                        return self.currentProject.payment.number_of_hits >= 1 && self.currentProject.payment.wage_per_hit >= 1 && self.currentProject.payment.charges >= 1;
                    }
                },
                {
                    id: 6, key: "review", name: "Summary",
                    is_dirty: false, is_valid: false,
                    validate: function () {
                        //TODO: validate all steps here again
                        return true;
                    }
                }
            ],
            currentStep: 1,
            init: function () {
                self.currentProject = {};
                self.currentProject.selectedCategory = self.currentProject.selectedCategory || null;
                self.currentProject.taskType = self.currentProject.taskType || 'oneTask';
                self.currentProject.payment = self.currentProject.payment || {};

                self.currentStep = 1;
            },
            getStep: function () {
                return this.steps[this.currentStep - 1];
            },
            setStep: function (stepId) {
                this.currentStep = stepId;
            },
            isFirstStep: function (stepId) {
                return stepId == 1;
            },
            isLastStep: function (stepId) {
                return stepId == this.steps.length;
            },
            getPrevious: function () {
                return this.isFirstStep(this.currentStep) ? 1 : this.currentStep - 1;
            },
            getNext: function () {
                return this.isLastStep(this.currentStep) ? this.currentStep : this.currentStep + 1;
            },
            validate: function (gotoNext) {
                var step = this.getStep();
                if (step.validate()) {
                    step.is_valid = true;
                    if (gotoNext) {
                        this.setStep(this.getNext());
                    }
                }
            }
        };

        // TODO: deprecate key based structure to allow flexibility
        self.form = {
            category: {is_expanded: false, is_done: false},
            general_info: {is_expanded: false, is_done: false},
            modules: {is_expanded: false, is_done: false},
            templates: {is_expanded: false, is_done: false},
            review: {is_expanded: false, is_done: false}
        };

        self.myProjects = [];
        self.getStatusName = getStatusName;
        self.monitor = monitor;

        self.other = false;
        self.otherIndex = 7;

        self.getPath = function () {
            return $location.path();
        };

        activate();

        function activate() {
            Project.getCategories().then(
                function success(resp) {
                    var data = resp[0];
                    self.categories = data;
                },
                function error(resp) {
                    var data = resp[0];
                    self.error = data.detail;
                }).finally(function () {
                });

            Project.getProjects().then(function (data) {
                self.myProjects = data[0];
            });
        }

        function getReferenceData() {
            Project.getReferenceData().success(function (data) {
                $scope.referenceData = data[0];
            });
        }

        /**
         * @name addProject
         * @desc Create new project
         * @memberOf crowdsource.project.controllers.ProjectController
         */
        function addProject() {
            self.currentProject.categories = [self.currentProject.selectedCategory.id];

            Project.addProject(self.currentProject).then(
                function success(resp) {
                    var data = resp[0];
                    console.log(self);
                    console.log($scope.projectForm);

                    self.wizard.init();
                    Project.clean();
                    $location.path('/monitor');
                },
                function error(resp) {
                    var data = resp[0];
                    self.error = data.detail;
                }).finally(function () {

                });
        }


        function getSelectedCategories() {
            return Project.selectedCategories;
        }

        function showTemplates() {
            return self.wizard.steps[0].is_valid;
        }

        function closeSideNav() {
            $mdSidenav('right').close()
                .then(function () {
                });
        }

        function finishModules() {
            self.form.modules.is_done = true;
            self.form.modules.is_expanded = false;
            if (!self.showTemplates()) {
                self.form.review.is_expanded = true;
            } else {
                self.form.templates.is_expanded = true;
            }

        }

        function activateTemplate(template) {
            self.selectedTemplate = template;
        }

        function addTemplate() {
            self.form.templates.is_done = true;
            self.form.templates.is_expanded = false;
            self.form.review.is_expanded = true;
        }

        function addModule() {
            var module = {
                name: self.module.name,
                description: self.module.description,
                repetition: self.module.repetition,
                dataSource: self.module.datasource,
                startDate: self.module.startDate,
                endDate: self.module.endDate,
                workerHelloTimeout: self.module.workerHelloTimeout,
                minNumOfWorkers: self.module.minNumOfWorkers,
                maxNumOfWorkers: self.module.maxNumOfWorkers,
                tasksDuration: self.module.tasksDuration,
                milestone0: {
                    name: self.module.milestone0.name,
                    description: self.module.milestone0.description,
                    allowRevision: self.module.milestone0.allowRevision,
                    allowNoQualifications: self.module.milestone0.allowNoQualifications,
                    startDate: self.module.milestone0.startDate,
                    endDate: self.module.milestone0.endDate
                },
                milestone1: {
                    name: self.module.milestone1.name,
                    description: self.module.milestone1.description,
                    startDate: self.module.milestone1.startDate,
                    endDate: self.module.milestone1.endDate
                },
                numberOfTasks: self.module.numberOfTasks,
                taskPrice: self.module.taskPrice
            };
            self.modules.push(module);
        }


        function computeTotal(payment) {
            var total = ((payment.number_of_hits * payment.wage_per_hit) + (payment.charges * 1));
            total = total ? total.toFixed(2) : '0.00';
            return total;
        }

        $scope.$watch('project.currentProject.payment', function (newVal, oldVal) {
            if (!angular.equals(newVal, oldVal)) {
                self.currentProject.payment.total = computeTotal(self.currentProject.payment);
            }

        }, true);

        $scope.$on("$destroy", function () {
            Project.syncLocally(self.currentProject);
        });

        function isSelected(item) {
            return !(self.selectedItems.indexOf(item) < 0);
        }

        function sort(header) {
            var sortedData = $filter('orderBy')(self.myProjects, header, self.config.order === 'descending');
            self.config.order = (self.config.order === 'descending') ? 'ascending' : 'descending';
            self.config.order_by = header;
            self.myProjects = sortedData;
        }

        function loadMyProjects() {
            Projects.getMyProjects()
                .then(function success(data, status) {
                    self.myProjects = data.data;
                },
                function error(data, status) {

                }).finally(function () {

                }
            );
        }

        function getProject() {
            var project = Project.retrieve();
            project.selectedCategory = project.selectedCategory || null;
            project.taskType = project.taskType || 'oneTask';
            project.payment = project.payment || {};

            return project;
        }

        function getStatusName(status) {
            return status == 1 ? 'created' : (status == 2 ? 'in review' : (status == 3 ? 'in progress' : 'completed'));
        }

        function monitor(project) {
            window.location = 'monitor/' + project.id;
        }
    }
})();