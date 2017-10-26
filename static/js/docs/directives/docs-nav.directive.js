
(function () {
    'use strict';
    angular
        .module('crowdsource.docs.directives')
        .directive('docsNavigation', docsNavigation);

    function docsNavigation($parse, $sce, $compile) {
        return {
            restrict: 'A',
            replace: true,
            templateUrl: '/static/templates/docs/navigation.html',
            link: function (scope, element, attrs, ctrl) {

            }
        };
    }
})();
