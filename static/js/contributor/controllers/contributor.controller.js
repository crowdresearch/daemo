(function () {
    'use strict';

    angular
        .module('crowdsource.contributor.controllers')
        .controller('ContributorController', ContributorController);

    ContributorController.$inject = ['$location', '$timeout', '$mdToast', 'Contributor', '$routeParams'];

    /**
     * @namespace ContributorController
     */
    function ContributorController($location, $timeout, $mdToast, Contributor, $routeParams) {
        var self = this;
        activate();

        function activate() {
            self.highlighted = Contributor.getHighlighted();

            var contributors = Contributor.getAll();

            self.contributors = _.groupBy(_.sortBy(contributors, 'name'), function(contributor){
                return contributor.name.charAt(0).toUpperCase();
            });

            var chars = "A,B,C,D,E,F,G,H,I,J,K,L,M,N,O,P,Q,R,S,T,U,V,W,X,Y,Z".split(',');
            self.allowed_chars = _.filter(chars, function(character){
                return self.contributors[character];
            });
        }
    }
})();
