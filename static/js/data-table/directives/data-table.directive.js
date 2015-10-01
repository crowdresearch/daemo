/**
* Data table directive
* @namespace crowdsource.data-table.directives
*/
(function () {
    'use strict';

    angular
      .module('crowdsource.data-table.directives')
      .directive('mdDataTable', mdDataTableDirective);
    angular
      .module('crowdsource.data-table.directives')
      .directive('mdDataTableCardHeader', mdDataTableCardHeaderDirective);
    angular
      .module('crowdsource.data-table.directives')
      .directive('mdDataTableCardHeaderTitle', mdDataTableCardHeaderTitleDirective);
    angular
        .module('crowdsource.data-table.directives')
        .directive('mdSortable', mdSortableDirective);
    function mdDataTableDirective(){
        return {
            restrict: 'E',
            transclude: false,
            scope: true

        };
    }
    function mdDataTableCardHeaderDirective(){
        return {
            restrict: 'E',
            transclude: false,
            //template: '1 item selected',
            scope: true,
            require: '^mdDataTable'
        };
    }

    function mdDataTableCardHeaderTitleDirective(){
        return {
            restrict: 'E',
            transclude: false,
            template: '1 item selected',
            scope: true,
            require: '^mdDataTableCardHeader'
        };
    }
    function mdSortableDirective(){
        return {
            restrict: 'EA',
            transclude: false,
            scope: false,
            link: function(scope, element, attrs){

            }
        };
    }
})();