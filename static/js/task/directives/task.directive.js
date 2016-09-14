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
                        } else {
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


/**
 * responseDirective
 * @namespace crowdsource.task.directives
 */
(function () {
    'use strict';
    angular
        .module('crowdsource.task.directives')
        .directive('taskResponse', taskResponse);
    function hasOptions(item) {
        return item.aux_attributes.hasOwnProperty('options');
    }

    function taskResponse($compile, Task, TaskWorker, Template, $filter) {
        return {
            restrict: "EA",
            scope: {
                taskId: '='
            },
            link: function (scope, element, attributes) {
                scope.hasOptions = hasOptions;
                scope.taskWorkers = [];
                Task.getPeerReviewTask(scope.taskId).then(function (data) {
                    var taskWorkerIds = data[0].task_workers;
                    TaskWorker.getTaskWorker(taskWorkerIds[0]).then(function (data) {
                        data[0].worker_alias = 'top submission';
                        scope.taskWorkers.push(data[0]);
                        TaskWorker.getTaskWorker(taskWorkerIds[1]).then(function (innerData) {
                            innerData[0].worker_alias = 'bottom submission';
                            scope.taskWorkers.push(innerData[0]);
                            Template.getTemplate("peer-review").then(function (template) {
                                var el = angular.element(template);
                                element.html(el);
                                $compile(el)(scope);
                            });
                        });
                    });
                });
            }
        }
    }
})();
