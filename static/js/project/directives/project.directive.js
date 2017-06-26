(function () {
    'use strict';

    angular
        .module('crowdsource.project.directives', [])
        .directive('projectPreview', projectPreview);

    function projectPreview(Project) {
        return {
            replace: true,
            templateUrl: '/static/templates/project/public-preview.html',
            restrict: 'A',
            scope: {
                projectPreview: '='
            },
            link: function (scope, elem, attrs, ctrl) {
                scope.projectId = scope.projectPreview;

                Project.getPreview(scope.projectId).then(
                    function success(data) {
                        scope.previewedProject = data[0];
                    },
                    function error(errData) {
                    }
                ).finally(function () {
                });
            }
        };
    }


})();
