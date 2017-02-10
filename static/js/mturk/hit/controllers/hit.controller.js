(function () {
    'use strict';

    angular
        .module('mturk.hit.controllers', [])
        .controller('HITController', HITController);

    HITController.$inject = ['$scope', '$state', '$mdToast', 'HIT', '$filter', '$sce', '$websocket', '$rootScope', '$stateParams', '$location', '$timeout'];

    function HITController($scope, $state, $mdToast, HIT, $filter, $sce, $websocket, $rootScope, $stateParams, $location, $timeout) {
        var self = this;
        self.isAccepted = false;
        self.submit = submit;
        self.currentStatus = false;
        self.pk = null;
        self.MTURK_HOST = 'https://workersandbox.mturk.com/mturk/externalSubmit';
        self.getHost = getHost;
        self.showSubmit = showSubmit;
        self.showTruth = showTruth;
        self.submitMturk = submitMturk;
        self.showRejectForm = false;
        self.notAllowed = false;
        self.noErrors = false;
        self.rejectionReason = null;
        self.rejectionDetail = null;
        self.rejectHIT = rejectHIT;
        self.HITRejected = false;
        self.hasTruth = false;
        self.notify = true;
        self.updateNotificationPreferences = updateNotificationPreferences;

        activate();


        self.reject_reason = {
            REASON_LOW_PAY: 1,
            REASON_INAPPROPRIATE: 2,
            OTHER: 3
        };

        function stringify(obj) {
            function flatten(obj) {
                if (_.isObject(obj)) {
                    return _.sortBy(_.map(
                        _.pairs(obj),
                        function (p) {
                            return [p[0], flatten(p[1])];
                        }
                        ),
                        function (p) {
                            return p[0];
                        }
                    );
                }
                return obj;
            }

            var converted = JSON.parse(angular.toJson(obj));
            return JSON.stringify(flatten(converted));
        }

        function activate() {
            var hitId = $stateParams.hitId;
            var assignmentId = $stateParams.assignmentId;
            self.assignmentId = assignmentId;
            var workerId = $stateParams.workerId;
            var taskId = $stateParams.taskId;

            HIT.get_or_create(taskId, hitId, assignmentId, workerId).then(
                function success(response) {
                    self.taskData = response[0].task;
                    self.is_review = response[0].is_review;
                    self.HITRejected = response[0].is_rejected;
                    self.task_id = self.taskData.id;
                    self.pk = response[0].assignment;
                    self.isAccepted = assignmentId !== 'ASSIGNMENT_ID_NOT_AVAILABLE';

                    if (self.isAccepted) {
                        var iframes = $filter('filter')(self.taskData.template.items, {type:'iframe'});

                        if(iframes.length>0)
                        {
                            initializeWebSocket();
                        }
                    }
                    self.noErrors = true;

                    if (response[0].hasOwnProperty('notify')) {
                        self.notify = response[0].notify;
                    }

                },
                function error(response) {
                    if (response[1] == 403) {
                        self.notAllowed = true;
                        return;
                    }
                    self.noErrors = false;
                    $mdToast.showSimple('Something went wrong, please try again.');
                }
            ).finally(function () {
            });

            HIT.get_url().then(
                function success(response) {
                    self.MTURK_HOST = response[0].url;
                },
                function error(response) {
                    $mdToast.showSimple('Could not get worker host.');
                }
            ).finally(function () {

            });
        }

        function submit() {
            var itemsToSubmit = $filter('filter')(self.taskData.template.items, {role: 'input'});
            var itemAnswers = [];
            var missing = false;

            self.status = {
                RETURNED: 5,
                REJECTED: 4,
                ACCEPTED: 3,
                SUBMITTED: 2,
                CREATED: 1
            };

            var finalAnswer = {};

            angular.forEach(itemsToSubmit, function (obj) {
                if ((!obj.answer || obj.answer == "") && obj.type != 'checkbox') {
                    missing = true;
                }

                if (obj.type != 'checkbox') {
                    itemAnswers.push(
                        {
                            template_item: obj.id,
                            result: obj.answer || ""
                        }
                    );

                    finalAnswer[obj.name] = obj.answer || "";
                }
                else {
                    itemAnswers.push(
                        {
                            template_item: obj.id,
                            result: obj.aux_attributes.options
                        }
                    );

                    finalAnswer[obj.name] = obj.aux_attributes.options;
                }
            });

            if (missing) {
                $mdToast.showSimple('All fields are required.');
                return;
            }

            var requestData = {
                task: self.taskData.id,
                items: itemAnswers,
                worker_id: $stateParams.workerId,
                assignment_id: $stateParams.assignmentId,
                hit_id: $stateParams.hitId
            };

            HIT.submit_results(self.pk, requestData).then(
                function success(response, status) {
                    self.currentStatus = true;
                    var data = response[0];

                    if (data.hasOwnProperty("message") && data.message == "truth") {
                        self.hasTruth = true;

                        self.truth = {};
                        var truthAnswer = {};
                        var items = angular.copy(self.taskData.template.items);

                        self.truth.items = _.map(items, function (item) {
                            if (item.role == 'input') {
                                if (data.hasOwnProperty("truth") && data.truth.hasOwnProperty(item.name)) {

                                    if (item.type != 'checkbox') {
                                        item.answer = data.truth[item.name];
                                        truthAnswer[item.name] = data.truth[item.name] || "";
                                    } else {
                                        var correctChoices = data.truth[item.name];

                                        item.aux_attributes.options = _.map(item.aux_attributes.options, function (option) {
                                            delete option.answer;

                                            if (correctChoices.indexOf(option.value) >= 0) {
                                                option.answer = true;
                                            }
                                            return option;
                                        });

                                        truthAnswer[item.name] = item.aux_attributes.options;
                                    }
                                }
                            }

                            return item;
                        });

                        self.truth.match = (stringify(finalAnswer) === stringify(truthAnswer));

                        $timeout(function () {
                            submitMturk();
                        }, 10000);

                    } else {
                        submitMturk();
                    }
                },
                function error(data, status) {
                    $mdToast.showSimple('Could not submit task!');

                }).finally(function () {
                }
            );
        }

        function getHost() {
            return $sce.trustAsResourceUrl(self.MTURK_HOST);
        }

        function showSubmit() {
            if (self.isAccepted && !self.currentStatus) {
                return $filter('filter')(self.taskData.template.items, {role: 'input'}).length > 0 && self.noErrors;
            }
            return false;
        }

        function showTruth() {
            return self.isAccepted && self.currentStatus && self.hasTruth;
        }

        function submitMturk() {
            $('#mturkForm').submit();
        }

        function initializeWebSocket() {
            self.ws = $websocket.$new({
                url: $rootScope.getWebsocketUrl() + '/ws/external?subscribe-broadcast',
                lazy: true,
                reconnect: true
            });

            self.ws
                .$on('$message', function (data) {
                    receiveMessage(data);
                })
                .$on('$close', function () {

                })
                .$on('$open', function () {
                    console.log('opened');
                })
                .$open();
        }

        function receiveMessage(data) {
            if (!self.taskData) {
                return;
            }
            var message = JSON.parse(data);
            if ($location.search().taskId != message.task_id) return;
            var inputItems = $filter('filter')(self.taskData.template.items, {role: 'input'});
            var remoteContentItems = $filter('filter')(self.taskData.template.items, {type: 'iframe'});
            var item = $filter('filter')(self.taskData.template.items, {id: message.template_item});
            if (inputItems.length == 0 && item.length && item[0].aux_attributes.src.indexOf(message.daemo_id) > 0) {
                item[0].isSubmitted = true;
                var submitted = $filter('filter')(self.taskData.template.items, {
                    isSubmitted: true,
                    type: 'iframe'
                });
                if (remoteContentItems.length == submitted.length) {
                    self.submit();
                }
            }
            $scope.$apply();
        }

        function rejectHIT() {
            if (!self.rejectionReason) {
                $mdToast.showSimple('Please choose a reason');
                return;
            }

            if (self.rejectionReason == self.reject_reason.OTHER && (!self.rejectionDetail || self.rejectionDetail == '')) {
                $mdToast.showSimple('Please provide details for flagging');
                return;
            }

            var request_data = {
                worker_id: $stateParams.workerId,
                assignment_id: $stateParams.assignmentId,
                hit_id: $stateParams.hitId,
                reason: self.rejectionReason,
                detail: self.rejectionDetail
            };

            HIT.reject(self.pk, request_data).then(
                function success(data, status) {
                    self.HITRejected = true;
                },
                function error(data, status) {
                    $mdToast.showSimple("Could not reject HIT!");
                }).finally(function () {
                }
            );
        }

        function updateNotificationPreferences(notify, projectId) {
            var workerId = $stateParams.workerId;
            HIT.updatePreferences(self.pk, {
                'notify': notify,
                'project_id': projectId,
                'worker_id': workerId
            }).then(function () {
            });
        }
    }
})
();


