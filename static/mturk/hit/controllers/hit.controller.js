(function () {
    'use strict';

    angular
        .module('mturk.hit.controllers', [])
        .controller('HITController', HITController);

    HITController.$inject = ['$scope', '$location', '$mdToast', 'HIT'];

    function HITController($scope, $location, $mdToast, HIT) {
        var self = this;
        self.isAccepted = false;
        activate();
        function activate() {
            var hitId = $location.search().hitId;
            var assignmentId = $location.search().assignmentId;
            var workerId = $location.search().workerId;
            var taskId = $location.search().taskId;
            HIT.get_or_create(taskId, hitId, assignmentId, workerId).then(
                function success(response) {
                    self.taskData = response[0];
                    self.isAccepted = assignmentId !== 'ASSIGNMENT_ID_NOT_AVAILABLE';
                },
                function error(response) {
                    $mdToast.showSimple('Could not get task data.');
                }
            ).finally(function () {
            });

        }
    }
})();


