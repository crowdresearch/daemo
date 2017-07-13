(function () {
    'use strict';

    angular
        .module('crowdsource.task.controllers')
        .controller('TaskReviewController', TaskReviewController);

    TaskReviewController.$inject = ['$scope', '$state', '$mdToast', '$stateParams',
        'Task'];

    function TaskReviewController($scope, $state, $mdToast, $stateParams, Task) {
        var self = this;
        self.task_worker = null;

        activate();

        function activate() {
            self.task_worker_id = $stateParams.taskWorkerId;

            Task.preview(self.task_worker_id).then(function success(data) {
                    self.loading = false;
                    self.task_worker = data[0];
                },
                function error(data) {
                    self.loading = false;
                    $mdToast.showSimple('Could not get task with data.');
                });
        }

    }
})();
