(function () {
    'use strict';

    angular
        .module('crowdsource.project.controllers')
        .controller('MyProjectController', MyProjectController);

    MyProjectController.$inject = ['$window', '$location', '$scope', '$mdToast', 'Project',
        '$filter', '$routeParams', 'Authentication'];

    /**
     * @namespace MyProjectController
     */
    function MyProjectController($window, $location, $scope, $mdToast, Project,
                               $filter, $routeParams, Authentication) {
        var self = this;
        self.myProjects = [];
        activate();
        function activate(){
            Project.getRequesterProjects().then(
                function success(response) {
                    self.myProjects = response[0];
                },
                function error(response) {

                }
            ).finally(function () {});
        }
    }
})();