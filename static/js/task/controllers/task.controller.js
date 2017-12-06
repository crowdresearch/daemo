(function () {
    'use strict';

    angular
        .module('crowdsource.task.controllers')
        .controller('TaskController', TaskController);

    TaskController.$inject = ['$scope', '$state', '$mdToast', '$log', '$http', '$stateParams',
        'Task', 'Authentication', 'Template', '$sce', '$filter', '$rootScope', 'RatingService',
        '$cookies', 'User', 'Upload', 'Project'];

    function TaskController($scope, $state, $mdToast, $log, $http, $stateParams, Task, Authentication,
                            Template, $sce, $filter, $rootScope, RatingService, $cookies, User, Upload, Project) {
        var self = this;

        var userAccount = Authentication.getAuthenticatedAccount();

        self.taskData = null;
        self.upload = upload;
        self.clearFiles = clearFiles;
        self.skip = skip;
        self.setRating = setRating;
        self.getMinWage = getMinWage;
        self.submitOrSave = submitOrSave;
        self.showRejectForm = false;
        self.saveComment = saveComment;
        self.openChat = openChat;
        self.loading = false;
        self.updateUserPreferences = updateUserPreferences;
        self.progressPercentage = 0;
        self.timeEstimates = {};
        self.rejectionReason = null;
        self.rejectionDetail = null;
        self.rejected = false;
        self.rejectTask = rejectTask;
        self.getTimeFormat = getTimeFormat;
        self.isReadyToLaunch = null;
        self.feedback = null;
        self.overrideReturn = overrideReturn;
        self.hasIframe = false;
        self.reject_reason = {
            REASON_LOW_PAY: 1,
            REASON_INAPPROPRIATE: 2,
            OTHER: 3
        };
        self.projectId = null;
        self.feedbackId = null;
        activate();

        function activate() {

            self.task_worker_id = $stateParams.taskWorkerId;
            self.task_id = $stateParams.taskId;

            self.isReturned = $stateParams.hasOwnProperty('returned');


            var id = self.task_id;

            if (self.isSavedQueue || self.isSavedReturnedQueue) {
                id = self.task_worker_id;
            }

            Task.getTaskWithData(self.task_id).then(function success(data) {
                    if (data[0].hasOwnProperty('requester_rating')) {
                        self.rating = data[0].requester_rating;
                    } else {
                        self.rating = {};
                    }
                    self.rating.project = data[0].project;
                    self.projectId = data[0].project;
                    if (data[0].data) {
                        $rootScope.pageTitle = data[0].data.project_data.name;
                    }

                    self.requester_alias = data[0].requester_alias;
                    self.taskData = data[0].data;
                    self.taskData.template.items = sortItems(data[0].data.template.items);
                    self.is_review = data[0].is_review;
                    self.is_qualified = data[0].is_qualified;
                    self.rejected = data[0].is_rejected;
                    self.return_feedback = data[0].return_feedback;
                    self.time_left = data[0].time_left;
                    self.task_worker_id = data[0].task_worker_id;
                    self.taskData.id = self.taskData.task ? self.taskData.task : id;
                    self.loading = false;
                    if (data[0].hasOwnProperty('auto_accept')) {
                        self.auto_accept = data[0].auto_accept;
                    } else {
                        self.auto_accept = false;
                    }
                    getTimeEstimates();
                    self.hasIframe = $filter('filter')(self.taskData.template.items, {type: 'iframe'}).length > 0;
                    Project.getFeedback(data[0].project).then(
                        function success(data) {
                            self.feedbackId = data[0].comment.id;
                            self.feedback = data[0].comment.body;
                            self.isReadyToLaunch = data[0].ready_for_launch;
                        },
                        function error(data) {

                        }).finally(function () {

                        }
                    );
                },
                function error(data) {
                    self.loading = false;
                    $mdToast.showSimple('Could not get task with data.');
                });

        }

        function getTimeFormat(seconds) {
            if (seconds < 60) {
                return 'seconds';
            }
            else if (seconds > 60 && seconds < 3600) {
                return 'minutes';
            }
            else {
                return 'hours';
            }
        }

        function skip() {
            self.loading = true;
            if (self.isSavedQueue || self.isSavedReturnedQueue) {
                Task.dropSavedTasks({task_ids: [self.task_id]}).then(
                    function success(data) {
                        gotoLocation(6, data);
                    },
                    function error(data) {
                        $mdToast.showSimple('Could not skip task.');
                    }).finally(function () {

                    }
                );
            } else {
                Task.skipTask(self.task_worker_id).then(
                    function success(data) {
                        self.loading = false;
                        gotoLocation(6, data);
                    },
                    function error(data) {
                        self.loading = false;
                        $mdToast.showSimple('Could not skip task.');
                    }).finally(function () {

                    }
                );
            }
        }

        function clearFiles(item) {
            item.answer = null;
        }

        function upload(files, template_item_id) {
            if (files && files.length) {
                self.fileUploading = true;
                for (var i = 0; i < files.length; i++) {
                    var file = files[i];

                    Upload.upload({
                        url: '/api/task-worker-result/upload-file/',
                        file: file
                    }).progress(function (evt) {
                        self.progressPercentage = parseInt(100.0 * evt.loaded / evt.total);

                        // console.log('progress: ' + progressPercentage + '% ' + evt.config.file.name);
                    }).success(function (data, status, headers, config) {
                        Task.attachFile(self.task_worker_id, template_item_id, data.id).then(
                            function success(response) {
                                var templateItem = $filter('filter')(self.taskData.template.items,
                                    {id: template_item_id});
                                if (templateItem.length) {
                                    templateItem[0].answer = response[0];
                                }
                                //self.taskData.template.items
                            },
                            function error(response) {
                            }
                        );
                    }).error(function (data, status, headers, config) {
                    })
                }
            }
        }

        function submitOrSave(status) {
            var itemsToSubmit = $filter('filter')(self.taskData.template.items, {role: 'input'});
            var itemAnswers = [];
            var missing = false;

            angular.forEach(itemsToSubmit, function (obj) {
                if ((!obj.answer || obj.answer === "") && obj.type !== 'checkbox' && obj.answer !== 0) {
                    if (obj.required) {
                        missing = true;
                    }
                } else {
                    if (obj.type === 'file_upload') return;
                    if (obj.type !== 'checkbox') {
                        itemAnswers.push(
                            {
                                template_item: obj.id,
                                result: obj.answer.toString() || ""
                            }
                        );
                    }
                    else {
                        itemAnswers.push(
                            {
                                template_item: obj.id,
                                result: obj.aux_attributes.options
                            }
                        );
                    }
                }
            });

            if (missing && status === 2) {
                $mdToast.showSimple('Not all required fields have been completed.');
                return;
            }
            /*
            if (self.taskData.project_data.is_prototype) {
                if (!self.feedback || self.feedback === '' || self.isReadyToLaunch === null) {
                    $mdToast.showSimple('Please provide feedback for this project.');
                    return;
                }
                postProjectComment();
            }
            */
            var requestData = {
                task: self.taskData.id,
                items: itemAnswers,
                status: status,
                saved: self.isSavedQueue || self.isSavedReturnedQueue,
                auto_accept: self.auto_accept
            };

            Task.submitTask(requestData).then(
                function success(data) {
                    gotoLocation(status, data);
                },
                function error(data) {
                    if (status === 1) {
                        $mdToast.showSimple('Could not save task.');
                    } else {
                        if (data[0].hasOwnProperty('message')) {
                            $mdToast.showSimple(data[0].message);
                        }
                        else {
                            $mdToast.showSimple('Could not submit task.');
                        }
                        $mdToast.showSimple('Could not submit task.');
                    }
                }).finally(function () {
                }
            );
        }

        function postProjectComment() {
            if (!self.feedbackId) {
                Project.postComment(self.projectId, self.feedback, self.isReadyToLaunch).then(
                    function success(data) {
                        console.log(data[0]);
                    },
                    function error(errData) {
                        $mdToast.showSimple('Error saving your feedback!');
                    }
                ).finally(function () {
                });
            }
            else {
                Project.updateComment(self.projectId, self.feedback, self.isReadyToLaunch).then(
                    function success(data) {

                    },
                    function error(errData) {
                        $mdToast.showSimple('Error saving your feedback!');
                    }
                ).finally(function () {
                });
            }

        }

        function saveComment() {
            Task.saveComment(self.taskData.id, self.comment.body).then(
                function success(data) {
                    if (!self.taskData.comments) {
                        angular.extend(self.taskData, {'comments': []});
                    }
                    self.taskData.comments.push(data[0]);
                    self.comment.body = null;
                },
                function error(errData) {
                    var err = errData[0];
                    $mdToast.showSimple('Error saving comment - ' + JSON.stringify(err));
                });
        }

        function gotoLocation(task_status, data) {

            if (task_status === 1 || data[1] !== 200) { //task is saved or failure
                $state.go('task_feed');
            } else if (task_status === 2 || task_status === 6) { //submit or skip
                if (self.auto_accept && data[0].task != self.taskData.id) {
                    $state.go('task', {taskId: data[0].task});
                } else {
                    $state.go('task_feed');
                }
            }

        }

        function openChat(requester) {
            $rootScope.openChat(requester);
        }

        function updateUserPreferences(auto_accept) {
            User.updatePreferences(userAccount.username, {'auto_accept': auto_accept}).then(function () {
            });
        }

        function setRating(rating, weight) {
            RatingService.updateProjectRating(weight, rating, self.taskData.project_data.id).then(function success(resp) {
                rating.weight = weight;
            }, function error(resp) {
                $mdToast.showSimple('Could not update rating.');
            }).finally(function () {

            });

        }

        function getTimeEstimates() {
            Project.getTimeEstimates(self.taskData.project_data.id).then(
                function success(response) {
                    self.timeEstimates = response[0];
                }, function error(resp) {
                }).finally(function () {
            });
        }

        function rejectTask() {
            if (!self.rejectionReason) {
                $mdToast.showSimple('Please choose a reason');
                return;
            }
            if (self.rejectionReason == self.reject_reason.OTHER
                && (!self.rejectionDetail || self.rejectionDetail === '')) {
                $mdToast.showSimple('Please provide details for flagging');
                return;
            }
            var requestData = {
                reason: self.rejectionReason,
                detail: self.rejectionDetail
            };
            Task.reject(self.task_worker_id, requestData).then(
                function success(data) {
                    self.rejected = true;
                },
                function error(errData) {
                    $mdToast.showSimple('An error occurred while rejecting this task.');
                });
        }

        function getMinWage() {
            var p = self.taskData.project_data.price / 10.5;
            if (p > 0.017) {
                return Math.round((p * 60)).toString() === '1' ? '1 minute' : Math.round((p * 60)).toString() + ' minutes';
            }
            return Math.round((p * 60) * 60).toString() + ' seconds';
        }

        function sortItems(items) {
            var results = [];
            var firstItems = $filter('filter')(items, {predecessor: null});
            angular.forEach(firstItems, function (item) {
                results.push(item);
                var next = $filter('filter')(items, {predecessor: item.id});
                while (next && next.length) {
                    var temp = next.pop();
                    results.push(temp);
                    var successors = $filter('filter')(items, {predecessor: temp.id});
                    if (successors && successors.length) {
                        angular.forEach(successors, function (obj) {
                            next.push(obj);
                        })
                    }
                }
            });
            return results;
        }

        function overrideReturn() {
            Task.overrideReturn(self.task_worker_id).then(
                function success(data) {
                    $state.go('task_feed');
                },
                function error(errData) {
                    $mdToast.showSimple('An error occurred while reporting the returned task.');
                });
        }


    }
})();
