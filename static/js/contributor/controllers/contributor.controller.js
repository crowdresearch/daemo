(function () {
    'use strict';

    angular
        .module('crowdsource.contributor.controllers')
        .controller('ContributorController', ContributorController);

    ContributorController.$inject = ['$state', '$timeout', '$mdToast', 'Contributor'];

    /**
     * @namespace ContributorController
     */
    function ContributorController($state, $timeout, $mdToast, Contributor) {
        var self = this;
        activate();

        function activate() {
            var chars = "A,B,C,D,E,F,G,H,I,J,K,L,M,N,O,P,Q,R,S,T,U,V,W,X,Y,Z".split(',');

            Contributor.getAll().success(
                function (response) {
                    var contributors = _.sortBy(_.map(_.filter(response, function (member) {
                            return member.author || member.active;
                        }), function (contributor) {
                            return {
                                name: contributor.name,
                                country: contributor.country,
                                author: contributor.author,
                                active: contributor.active,
                                photo: contributor.photo
                            };
                        }),
                        'name');

                    self.highlighted = _.filter(contributors, function (contributor) {
                        return contributor.author;
                    });


                    self.contributors = _.groupBy(_.filter(contributors, function (contributor) {
                        return contributor.active && !contributor.author;
                    }), function (contributor) {
                        return contributor.name.charAt(0).toUpperCase();
                    });

                    self.allowed_chars = _.filter(chars, function (character) {
                        return self.contributors.hasOwnProperty(character);
                    });
                });
        }
    }
})();
