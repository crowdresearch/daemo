/**
 * Created by sehgalvibhor on 02/02/16.
 */

/**
 * timerDirective
 * @namespace crowdsource.task.directives
 */
(function () {
    'use strict';
    angular
        .module('crowdsource.task.directives')
        .directive('timerCounter', timerCounter);

    function timerCounter($timeout) {
        return {
            restrict: "A",
            scope: {
                secondsLeft: "="
            },
            link: function (scope, element, attributes) {
                if (angular.isUndefined(attributes.secondsLeft)) {
                    throw "seconds-left value is not passed";
                }

                scope.$watch("secondsLeft", function (val) {
                    if (val != null) {
                        var secondsLeft = parseInt(val);

                        if (!isNaN(secondsLeft)) {
                            countdown(0, secondsLeft);
                        }else{
                            throw "seconds-left value must be integer";
                        }
                    }
                });

                function countdown(minutes, seconds) {
                    var endTime, hours, mins, msLeft, time;

                    function twoDigits(n) {
                        return (n <= 9 ? "0" + n : n);
                    }

                    function updateTimer() {
                        msLeft = endTime - (+new Date);
                        if (msLeft < 1) {
                            scope.timer = "Expired";
                            $timeout.cancel();
                        } else {
                            time = new Date(msLeft);
                            hours = time.getUTCHours();
                            mins = time.getUTCMinutes();
                            scope.timer = (hours ? hours + ':' + twoDigits(mins) : mins) + ':' + twoDigits(time.getUTCSeconds());
                            $timeout(updateTimer, time.getUTCMilliseconds() + 500);
                        }
                    }

                    endTime = (+new Date) + 1000 * (60 * minutes + seconds) + 500;
                    updateTimer();
                }
            },
            template: '{{ timer }}'
        };
    }
})();
