(function () {
    'use strict';

    angular
        .module('crowdsource.task.controllers')
        .controller('TaskController', TaskController);

    TaskController.$inject = ['$scope', '$state', '$mdToast', '$log', '$http', '$stateParams',
        'Task', 'Authentication', 'Template', '$sce', '$filter', '$rootScope', 'RatingService', '$cookies', 'User', 'Upload'];

    function TaskController($scope, $state, $mdToast, $log, $http, $stateParams, Task, Authentication, Template, $sce, $filter, $rootScope, RatingService, $cookies, User, Upload) {
        var self = this;

        var userAccount = Authentication.getAuthenticatedAccount();

        self.taskData = null;
        self.upload = upload;
        self.clearFiles = clearFiles;
        self.skip = skip;
        self.setRating = setRating;
        self.submitOrSave = submitOrSave;
        self.saveComment = saveComment;
        self.openChat = openChat;
        self.loading = false;
        self.updateUserPreferences = updateUserPreferences;
        self.progressPercentage = 0;

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
                    if(data[0].data){
                        $rootScope.pageTitle = data[0].data.project_data.name;
                    }

                    self.requester_alias = data[0].requester_alias;
                    self.taskData = data[0].data;
                    self.is_review = data[0].is_review;
                    self.is_qualified = data[0].is_qualified;
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

                },
                function error(data) {
                    self.loading = false;
                    $mdToast.showSimple('Could not get task with data.');
                });
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
                                if(templateItem.length){
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
                if ((!obj.answer || obj.answer === "") && obj.type !== 'checkbox') {
                    if (obj.required) {
                        missing = true;
                    }
                } else {
                    if(obj.type === 'file_upload') return;
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

        //     self.handleRatingSubmit = function (rating, entry) {
        //         if (entry.hasOwnProperty('current_rating_id')) {
        //             RatingService.updateRating(rating, entry).then(function success(resp) {
        //                 entry.current_rating = rating;
        //             }, function error(resp) {
        //                 $mdToast.showSimple('Could not update rating.');
        //             }).finally(function () {
        //
        //             });
        //         } else {
        //             entry.reviewType = 'worker';
        //             RatingService.submitRating(rating, entry).then(function success(resp) {
        //                 entry.current_rating_id = resp[0].id;
        //                 entry.current_rating = rating;
        //             }, function error(resp) {
        //                 $mdToast.showSimple('Could not submit rating.')
        //             }).finally(function () {
        //
        //             });
        //         }
        //     }
        function setRating(rating, weight) {
            RatingService.updateProjectRating(weight, rating, self.taskData.project_data.id).then(function success(resp) {
                rating.weight = weight;
            }, function error(resp) {
                $mdToast.showSimple('Could not update rating.');
            }).finally(function () {

            });

        }
    }
})();
