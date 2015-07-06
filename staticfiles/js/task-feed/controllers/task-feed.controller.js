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
      var userAccount = Authentication.getAuthenticatedAccount();
      if (!userAccount || !userAccount.profile) {
        $location.path('/login');
        return;
      }
      
      var self = this;
      self.toggleBookmark = toggleBookmark;
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
              id: 1,
              name: "Build a website using AngularJs",
              description: "Build a website using Python Django Framework, AngularJs and Material Design",
              category: "Programming",
              skills: "html, angularjs, python, django, css",
              tasks: 32,
              requester: 'neilg',
              time_to_complete: '2 days',
              is_bookmarked: true,
              pay: '$150'


          },
          {
              id: 2,
              name: "Help me write a research paper",
              description: "Topic of the paper is crowd sourcing platforms...",
              tasks: 23,
              category: "Writing",
              skills: "English, research",
              requester: 'dmorina',
              time_to_complete: '10 days',
              is_bookmarked: false,
              pay: '$256'
          },
          {
              id: 3,
              name: "Take my dire wolf for a walk",
              description: "A short walk around Winterfell",
              tasks: 13,
              category: "Reading",
              skills: "Walking, Dire wolf language",
              requester: 'jon.snow',
              time_to_complete: '4 hours',
              is_bookmarked: true,
              pay: '$20'
          },
          {
              id: 4,
              name: "Label galaxies",
              description: "Label images of galaxies using the predefined options",
              tasks: 47,
              category: "Data Science",
              skills: "None required",
              requester: 'rohitn',
              time_to_complete: '3 hours',
              is_bookmarked: false,
              pay: '$30'
          }
      ];
      function toggleBookmark(project){
          project.is_bookmarked = !project.is_bookmarked;
      }
  }

})();