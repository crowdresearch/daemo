/**
* RequesterTaskPortfolioController
* @namespace crowdsource.requester.services
*/
(function () {
  'use strict';

  angular
    .module('crowdsource.requester.services')
    .factory('RequesterTaskPortfolioController', RequesterTaskPortfolioController);

  RequesterTaskPortfolioController.$inject = ['$cookies', '$http', '$q', '$location'];

  /**
  * @namespace RequesterTaskPortfolioController
  * @returns {Factory}
  */

  function RequesterTaskPortfolioController($cookies, $http, $q, $location) {
    /**
    * @name RequesterTaskPortfolioController
    * @desc The Factory to be returned
    */
    var RequesterTaskPortfolioController = {
      
    };

    return RequesterTaskPortfolioController;
};

    
})();
