(function () {
    'use strict';

    angular
        .module('crowdsource.project.controllers')
        .controller('ProjectRatingController', ProjectRatingController);

    ProjectRatingController.$inject = ['$scope', 'Project', 'resolvedData', '$stateParams', 'Task', '$mdToast',
        '$filter', 'RatingService', '$mdDialog', '$state'];

    /**
     * @namespace ProjectRatingController
     */
    function ProjectRatingController($scope, Project, resolvedData, $stateParams, Task, $mdToast,
                                     $filter, RatingService, $mdDialog, $state) {
        var self = this;
        self.tasks = [];
        self.workers = [];
        self.loading = true;
        self.loadingSubmissions = true;
        self.submissions = [];
        self.resolvedData = {};
        self.getQuestionNumber = getQuestionNumber;
        self.hasOptions = hasOptions;
        self.isSelected = isSelected;
        self.selectedTaskId = null;
        self.taskData = null;
        self.selectedTask = null;
        self.setSelected = setSelected;
        self.getQuestion = getQuestion;
        self.getResult = getResult;
        self.getStatus = getStatus;
        self.setRating = setRating;
        self.showActions = showActions;
        self.selectedRevision = null;
        self.getRated = getRated;
        self.isRating = true;
        self.group_by = 'Task';
        self.sorted_by = 'created_at';

        function getRated() {
            return 0;
        }
        activate();
        function activate() {
            self.resolvedData = resolvedData[0];
            self.selectedRevision = self.resolvedData.id;
            self.revisions = self.resolvedData.revisions;
            Project.getWorkersToRate(self.resolvedData.id).then(
                function success(response) {
                    self.loading = false;
                    self.tasks = response[0];
                    self.workers = response[0];
                },
                function error(response) {
                    $mdToast.showSimple('Could not fetch workers to rate.');
                }
            ).finally(function () {
            });
        }

        function getQuestionNumber(list, item) {
            // get position if item is input type
            var position = '';

            if (item.role == 'input') {
                var inputItems = $filter('filter')(list,
                    {role: 'input'});

                position = _.findIndex(inputItems, function (inputItem) {
                        return inputItem.id == item.id;
                    }) + 1;
                position += ') ';
            }

            return position;
        }

        function hasOptions(item) {
            return item.aux_attributes.hasOwnProperty('options');
        }

        function isSelected(task) {
            return angular.equals(task, self.selectedTask);
        }

        function setSelected(item) {
            if (angular.equals(item, self.selectedTask)) {
                return null;
            }
            else {
                self.listSubmissions(item);
            }
        }

        function getQuestion(list, item) {
            return getQuestionNumber(list, item) + item.aux_attributes.question.value
        }

        function getResult(result) {
            var item = $filter('filter')(self.resolvedData.template.items,
                {id: result.template_item})[0];

            if (Object.prototype.toString.call(result.result) === '[object Array]') {
                return $filter('filter')(result.result, {answer: true}).map(function (obj) {
                    return obj.value;
                }).join(', ');
            }
            else if (item.type == 'iframe') {
                var resultSet = [];
                angular.forEach(result.result, function (value, key) {
                    resultSet.push(key + ': ' + value);
                });
                resultSet = resultSet.join(', ');

                return getQuestionNumber(self.resolvedData.template.items, item) + resultSet;
            }
            else {
                return getQuestionNumber(self.resolvedData.template.items, item) + result.result;
            }
        }


        function getStatus(statusId) {
            for (var key in self.status) {
                if (self.status.hasOwnProperty(key)) {
                    if (statusId == self.status[key])
                        return key;
                }

            }
        }


        function setRating(rating, weight) {
            if (rating && rating.hasOwnProperty('id') && rating.id) {
                RatingService.updateRating(weight, rating).then(function success(resp) {
                    rating.weight = weight;
                }, function error(resp) {
                    $mdToast.showSimple('Could not update rating.');
                }).finally(function () {

                });
            } else {
                RatingService.submitRating(weight, rating, self.selectedTask.id).then(function success(resp) {
                    rating.id = resp[0].id;
                    rating.weight = weight;
                }, function error(resp) {
                    $mdToast.showSimple('Could not submit rating.')
                }).finally(function () {

                });
            }
        }

        function showActions(workerAlias) {
            return workerAlias.indexOf('mturk') < 0;
        }
    }
})();
