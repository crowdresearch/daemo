/**
 * DemoController
 * @namespace crowdsource.layout.controllers
 */
(function () {
    'use strict';

    angular
        .module('crowdsource.layout.controllers')
        .controller('DemoController', DemoController);

    DemoController.$inject = ['$scope', '$rootScope', '$state', '$anchorScroll', 'Authentication'];

    /**
     * @namespace DemoController
     */
    function DemoController($scope, $rootScope, $state, $anchorScroll, Authentication) {
        var self = this;

        self.logout = logout;
        self.scrollTo = scrollTo;
        self.goTo = goTo;

        $scope.isLoggedIn = Authentication.isAuthenticated();
        $scope.account = Authentication.getAuthenticatedAccount();

        $scope.options = {
            chart: {
                type: 'lineChart',
                height: 350,
                x: function(d){ return d.x; },
                y: function(d){ return d.y; },
                useInteractiveGuideline: true,
                xAxis: {
                    axisLabel: 'Batch',
                    tickFormat: function(d){
                        return d3.format('.0f')(d);
                    }
                },
                yAxis: {
                    axisLabel: 'Accuracy',
                    tickFormat: function(d){
                        return d3.format('.0f')(d);
                    },
                    axisLabelDistance: -8
                }
            }
        };

        $scope.data = getData();

        function getData() {
            var daemo = [],
                mturk = [];

            //Data is represented as an array of {x,y} pairs.
            for (var i = 1; i < 10; i++) {
                daemo.push({x: i, y: Math.exp(0.06*i)*100/2});
                mturk.push({x: i, y: 50*Math.sin(9*i)+0.6});
            }

            //Line chart data should be sent as an array of series objects.
            return [
                {
                    values: daemo,      //values - represents the array of {x,y} data points
                    key: 'Daemo', //key  - the name of the series.
                    color: '#ff7f0e',  //color - optional: choose your own line color.
                    strokeWidth: 2
                },
                {
                    values: mturk,
                    key: 'Platform X',
                    color: '#fff',
                    strokeWidth: 2
                }
            ];
        };

        /**
         * @name logout
         * @desc Log the user out
         * @memberOf crowdsource.layout.controllers.DemoController
         */
        function logout() {
            $rootScope.closeWebSocket();

            Authentication.logout();
        }

        function goTo(state){
            $state.go(state);
        }
    }
})();
