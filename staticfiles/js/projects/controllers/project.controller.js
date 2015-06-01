/**
 * Project Controller
 * Author: Shirish Goyal
 */
(function () {
    'use strict';

    angular.module('crowdsource.projects.controllers', [
        'smart-table',
        'crowdsource.projects.services'
    ])
        .controller('ProjectController', ProjectController);

    ProjectController.$inject = ['$scope', '$log', 'ProjectService'];

    /**
     *
     * @param $scope
     * @param $log
     * @param ProjectService
     * @constructor
     */
    function ProjectController($scope, $log, ProjectService) {

        $scope.displayedCollection = [];
        $scope.rowCollection = [];

        ProjectService.list(50, 1)
            .then(function (data, config) {
                $scope.displayedCollection = data;
                $scope.rowCollection = data;
            },
            function (data, status, headers, config) {
            });

        $scope.gridOptionsTask = {
            multiSelect: false,
            enablePinning: true,
            data: 'project',
            columnDefs: [
                { field: "name", displayName: 'Name', width: 200, pinned: true },
                { field: "categories", displayName: 'Categories', width: 190 },
                { field: "price", displayName: 'Price', width: 60 },
                { field: "deadline", displayName: 'Deadline', width: 130 },
            ]
        };
    }

})();
