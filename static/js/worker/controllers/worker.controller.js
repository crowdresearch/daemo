/**
 * WorkerProfileController
 * @namespace crowdsource.worker.controllers
 */
(function () {
    'use strict';

    angular
        .module('crowdsource.worker.controllers')
        .controller('WorkerProfileController', WorkerProfileController);

    WorkerProfileController.$inject = ['$state', '$scope', 'Authentication', 'Worker', 'Skill'];

    /**
     * @namespace WorkerProfileController
     */
    function WorkerProfileController($state, $scope, Authentication, Worker, Skill) {
        var vm = this;

        var userAccount = Authentication.getAuthenticatedAccount();

        Skill.getAllSkills().then(function (skillsData) {
            $scope.skills = skillsData[0];
            getWorkerPrivatePortfolio();
        });

        Worker.getWorkerTaskPortfolio().success(function (data) {
            $scope.WorkerTaskPortfolio = data;
        });

        function getWorkerPrivatePortfolio() {
            Worker.getWorkerPrivateProfile(userAccount.profile.id)
                .then(function (data) {

                    $scope.user = data[0];
                    // Make worker id specific
                    $scope.user.workerId = $scope.user.id;
                    var refinedSkills = [];
                    $scope.user.skills.forEach(function (skillId) {
                        $scope.skills.forEach(function (skillEntry) {
                            if (skillId === skillEntry.id) {
                                refinedSkills.push(skillEntry);
                            }
                        });
                    });
                    $scope.user.skills = refinedSkills;
                    var numberOfRealTimeTasks = $scope.user.realTimeTaskProgress.length, count = 0;
                    for (var i = 0; i < numberOfRealTimeTasks; i++) {
                        if ($scope.user.realTimeTaskProgress[i].completed == true) {
                            count++;
                        }
                    }
                    $scope.progress = parseInt(count / numberOfRealTimeTasks * 100).toFixed(2);

                });
        }


    }
})();