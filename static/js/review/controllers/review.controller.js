(function () {
    'use strict';

    angular
        .module('crowdsource.review.controllers', [])
        .controller('ReviewController', ReviewController);

    ReviewController.$inject = ['$scope', '$state', '$mdToast', '$log', '$http', '$stateParams',
        'Task', 'Authentication', 'Template', '$sce', '$filter', '$rootScope', 'Review', '$cookies', 'User'];

    function ReviewController($scope, $state, $mdToast, $log, $http, $stateParams, Task, Authentication, Template, $sce, $filter, $rootScope, Review, $cookies, User) {
        var self = this;
        self.hasOptions = hasOptions;
        self.getQuestionNumber = getQuestionNumber;
        self.getResult = getResult;
        self.submit = submit;

        var userAccount = Authentication.getAuthenticatedAccount();

        activate();

        function activate() {

            self.id = $stateParams.reviewId;

            Review.get(self.id).then(function success(data) {
                    self.review = data[0];

                    if (self.review.hasOwnProperty('review_data') && self.review.review_data) {
                        var ratings = getRatingList(self.review.task_worker.worker_level);
                        self.review.review_data.rating_text = ratings[self.review.review_data.rating - 1];

                        self.review_ratings = getRatingList(self.review.worker_level);
                    } else {
                        self.review_ratings = getRatingList(self.review.task_worker.worker_level);
                    }
                },
                function error(data) {
                    $mdToast.showSimple('Could not get review');
                });
        }

        function hasOptions(item) {
            return item.aux_attributes.hasOwnProperty('options');
        }

        function getQuestionNumber(resultObj) {
            var item = $filter('filter')(self.review.task_worker.task_data.template.template_items,
                {id: resultObj.template_item})[0];
            return item.position;
        }

        function getResult(result) {
            var item = $filter('filter')(self.review.task_worker.task_data.template.template_items,
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
                return resultSet;
            }
            else {
                return result.result;
            }
        }

        function submit(isValid) {
            if (isValid) {
                Review.update(self.id, {
                    rating: self.review.rating,
                    is_acceptable: self.review.is_acceptable,
                    comment: self.review.comment
                }).then(function success(data, status) {
                    $state.transitionTo('task_feed');
                }, function error(data, status) {
                    vm.error = data.data.detail;
                    $scope.form.$setPristine();
                }).finally(function () {
                });
            }
        }

        function getRatingList(level) {
            var level = parseInt(level);
            return [
                'Underperforming for Level ' + level,
                'Appropriate for Level ' + level,
                'Good enough work to endorse for Level ' + (level + 1),
                'Good enough work to endorse for Level ' + (level + 2)
            ]
        }


    }
})();
