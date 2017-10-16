/**
 * HomeController
 * @namespace crowdsource.layout.controllers
 */
(function () {
    'use strict';

    angular
        .module('crowdsource.layout.controllers')
        .controller('HomeController', HomeController);

    HomeController.$inject = ['$scope', '$rootScope', '$state', '$anchorScroll', 'Authentication'];

    /**
     * @namespace HomeController
     */
    function HomeController($scope, $rootScope, $state, $anchorScroll, Authentication) {
        var self = this;

        self.logout = logout;
        self.scrollTo = scrollTo;
        self.goTo = goTo;
        self.getData = getData;

        $scope.isLoggedIn = Authentication.isAuthenticated();
        $scope.account = Authentication.getAuthenticatedAccount();

        $scope.randomImg = 1+Math.floor(Math.random() * 5);

        $scope.data = {
            'reddit': [{
                x: 1, y: 48.67
            }, {
                x: 2, y: 56.67
            }, {
                x: 3, y: 52.32
            }, {
                x: 4, y: 49.33
            }, {
                x: 5, y: 60.39
            }],
            'webpage': [{
                x: 1, y: 52
            }, {
                x: 2, y: 72.78
            }, {
                x: 3, y: 82.67
            }, {
                x: 4, y: 84.67
            }, {
                x: 5, y: 76.67
            }],
            'spot': [{
                x: 1, y: 92
            }, {
                x: 2, y: 96
            }, {
                x: 3, y: 93
            }, {
                x: 4, y: 86
            }, {
                x: 5, y: 79
            }],
            'image': [{
                x: 1, y: 70.20
            }, {
                x: 2, y: 73.33
            }, {
                x: 3, y: 76.67
            }, {
                x: 4, y: 70
            }, {
                x: 5, y: 78
            }],
            'marijuana': [{
                x: 1, y: 69.33
            }, {
                x: 2, y: 82
            }, {
                x: 3, y: 76
            }, {
                x: 4, y: 74.67
            }, {
                x: 5, y: 76.67
            }]
        };

        $scope.options = {
            chart: {
                type: 'lineChart',
                height: 300,
                x: function (d) {
                    return d.x;
                },
                y: function (d) {
                    return d.y;
                },
                useInteractiveGuideline: true,
                xAxis: {
                    axisLabel: 'Batch',
                    tickFormat: function (d) {
                        return d3.format('.0f')(d);
                    }
                },
                yAxis: {
                    axisLabel: 'Accuracy',
                    tickFormat: function (d) {
                        return d3.format('.0f')(d);
                    },
                    axisLabelDistance: -15
                },
                interpolate: 'basis',
                yDomain: [0, 100]

            }
        };

        $scope.chartData = {
            'reddit':getData('reddit'),
            'webpage':getData('webpage'),
            'spot':getData('spot'),
            'image':getData('image'),
            'marijuana':getData('marijuana')
        };

        function getData(label) {
            // if (label && $scope.data) {
                var daemo = $scope.data[label];

                //Line chart data should be sent as an array of series objects.
                return [
                    {
                        values: daemo,      //values - represents the array of {x,y} data points
                        key: 'daemo', //key  - the name of the series.
                        color: '#ff7f0e',  //color - optional: choose your own line color.
                        strokeWidth: 2
                    }
                    // {
                    //     values: mturk,
                    //     key: 'Platform X',
                    //     color: '#fff',
                    //     strokeWidth: 2
                    // }
                ];
            // }
        }

        /**
         * @name logout
         * @desc Log the user out
         * @memberOf crowdsource.layout.controllers.HomeController
         */
        function logout() {
            $rootScope.closeWebSocket();

            Authentication.logout();
        }

        function goTo(state) {
            $state.go(state);
        }
    }
})();
