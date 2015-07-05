/**
* TaskFeedController
* @namespace crowdsource.task-feed.controllers
 * @author dmorina
*/
(function () {
  'use strict';

  angular
    .module('crowdsource.task-feed.controllers')
    .controller('TaskFeedController', TaskFeedController);

  TaskFeedController.$inject = ['$window', '$location', '$scope', 'TaskFeed', '$filter', 'Authentication'];

  /**
  * @namespace TaskFeedController
  */
  function TaskFeedController($window, $location, $scope, TaskFeed, $filter, Authentication) {
      var vm = this;
      var userAccount = Authentication.getAuthenticatedAccount();
      if (!userAccount || !userAccount.profile) {
        $location.path('/login');
        return;
      }
      
      var self = this;
      self.modules = [];

      /*TaskFeed.getProjects().then(
        function success (successData) {
          var data = successData[0];
          data.forEach(function(item) {
            var project = {
              name: item.name,
              description: item.description,
              category: item.category,
              skills: item.keywords,
              tasks: 32,
              requester: 'Alan',
              pay: '$15/hr'
            };
            self.modules.push(project);
          });
        },
        function error(errData) {
          self.error = errData[0].detail;
        }
      ).finally(function () {});
       */
      
      self.modules = [
          {
              name: "Build a website using AngularJs",
              description: "Build a website using Python Django Framework, AngularJs and Material Design",
              category: "Programming",
              skills: "html, angularjs, python, django, css",
              tasks: 32,
              requester: 'neilg',
              time_to_complete: '2 days',
              pay: '$150'


          },
          {
              name: "Help me write a research paper",
              description: "Topic of the paper is crowd sourcing platforms...",
              tasks: 23,
              category: "Writing",
              skills: "English, research",
              requester: 'dmorina',
              time_to_complete: '10 days',
              pay: '$256'
          },
          {
              name: "Take my dire wolf for a walk",
              description: "A short walk around Winterfell",
              tasks: 13,
              category: "Reading",
              skills: "Walking, Dire wolf language",
              requester: 'jon.snow',
              time_to_complete: '4 hours',
              pay: '$20'
          },
          {
              name: "Label galaxies",
              description: "Label images of galaxies using the predefined options",
              tasks: 47,
              category: "Data Science",
              skills: "None required",
              requester: 'rohitn',
              time_to_complete: '3 hours',
              pay: '$30'
          }
      ];
      
  }

})();