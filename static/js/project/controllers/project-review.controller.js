(function () {
    'use strict';

    angular
        .module('crowdsource.project.controllers')
        .controller('ProjectReviewController', ProjectReviewController);

    ProjectReviewController.$inject = ['$scope', 'Project', 'projectData'];

    /**
     * @namespace ProjectReviewController
     */
    function ProjectReviewController($scope, Project, projectData) {
        var self = this;
        activate();
        function activate(){
            self.projectData = projectData[0];
        }


    }
})();
