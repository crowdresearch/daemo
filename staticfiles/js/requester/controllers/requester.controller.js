/**
* Requester Task Portfolio Controller
* @namespace crowdsource.requester.controllers
*/
(function () {
  'use strict';

  angular
    .module('crowdsource.requester.controllers')
    .controller('RequesterTaskPortfolioController', RequesterTaskPortfolioController);

  RequesterTaskPortfolioController.$inject = ['$location', '$scope', 'Authentication'];

  /**
  * @namespace HomeController
  */
  function RequesterTaskPortfolioController($location, $scope, Authentication) {
    var vm = this;

    $scope.user = {
      TaskCategories : [{
	   icon:'font-awesome-big-icon fa fa-file-image-o',
          name : 'Image Labeling',
          NoofTasks : 5,
	  reviews: 45,
	  stars :3
        },
        {
	  icon:'font-awesome-big-icon glyphicon glyphicon-pencil',
          name : 'Sentiment Analysis',
          NoofTasks : 25,
	  reviews: 5,
	  stars :2
        },
        {
	  icon:'font-awesome-big-icon glyphicon glyphicon-pencil',
          name : 'Academic Survey',
          NoofTasks : 35,
	  reviews: 75,
	  stars :5
        },
	 {
	  icon:'font-awesome-big-icon fa fa-camera',
          name : 'Photograph',
          NoofTasks : 15,
	  reviews: 40,
	  stars :1
        },
        {
	  icon:'font-awesome-big-icon fa fa-soundcloud',
          name : 'Audio Transcription',
          NoofTasks : 20,
	  reviews: 33,
	  stars :2
        },
	{
	 icon:'font-awesome-big-icon fa fa-table',
          name : 'Data Entry',
          NoofTasks : 12,
	  reviews: 34,
	  stars :4
        },
        {
	  icon:'font-awesome-big-icon fa fa-line-chart',
          name : 'Trend Analysis',
          NoofTasks : 30,
	  reviews: 22,
	  stars :3
        },
        
      ]
      
    };
 $scope.range = new Array(5);
$scope.convertToInt= function (value) {
            return parseInt(value);
        };
  }

})();
