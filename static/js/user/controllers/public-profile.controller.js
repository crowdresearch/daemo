(function () {
    'use strict';

    angular
        .module('crowdsource.user.controllers')
        .controller('PublicProfileController', PublicProfileController);

    PublicProfileController.$inject = ['$state', '$scope', '$mdToast', 'User', '$stateParams', 'RatingService'];

    function PublicProfileController($state, $scope, $mdToast, User, $stateParams, RatingService) {
        var self = this;
        self.goTo = goTo;
        self.user = null;
        self.loading = false;
        self.setRating = setRating;
        activate();

        function activate() {
            self.loading = true;
            User.getPublicProfile($stateParams.handle)
                .then(function (data) {
                        self.user = data[0];
                        self.loading = false;
                    },
                    function error(errData) {
                        $mdToast.showSimple('Error fetching profile.');
                        self.loading = false;
                    }
                );
        }

        function goTo(state) {
            $state.go(state, {});
        }

        function setRating(project, weight, originType) {
            var ratingObj = {
                "origin_type": originType,
                "target": this.user.id
            };
            RatingService.updateProjectRating(weight, ratingObj, project.id).then(function success(resp) {
                project.rating = weight;
            }, function error(resp) {
                $mdToast.showSimple('Could not update rating.');
            }).finally(function () {

            });
        }
    }
})();
