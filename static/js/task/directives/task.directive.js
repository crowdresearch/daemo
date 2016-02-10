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
        .directive('timerDirective', timerDirective);

    function timerDirective($timeout) {
        return {
            restrict: "A",
            scope: {
                text: "=myText",
            },              
            link: function(scope, element, attributes){
                    scope.$watch("text", function(val) {
                        if (scope.text != null)
                        {   
                            countdown(0,scope.text);
                        }                        
                    });
                    function countdown(minutes, seconds)
                    {   var endTime, hours, mins, msLeft, time;
                        function twoDigits( n )
                        {
                            return (n <= 9 ? "0" + n : n);
                        }

                        function updateTimer()
                        {
                            msLeft = endTime - (+new Date);
                            if ( msLeft < 1000 ) {
                                scope.timer = "Task Expired";
                                $timeout.cancel();
                            } else {
                                time = new Date( msLeft );
                                hours = time.getUTCHours();
                                mins = time.getUTCMinutes();
                                scope.timer = (hours ? hours + ':' + twoDigits( mins ) : mins) + ':' + twoDigits( time.getUTCSeconds() );
                                $timeout(updateTimer, time.getUTCMilliseconds() + 500);
                                }
                            }
                            endTime = (+new Date) + 1000 * (60*minutes + seconds) + 500;
                            updateTimer();
                        }
            },
            template: 'Time left : {{ timer }} '
        };
    }
})();
