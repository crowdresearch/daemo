(function () {
  'use strict';

  angular
    .module('crowdsource.requester', [
      'crowdsource.requester.controllers',
      'crowdsource.requester.services'
    ]);

  angular
    .module('crowdsource.requester.controllers', [])
    .directive('animm',function() {
      return {
            link: function(scope, el, attrs){
                setTimeout(function(){
                    var progressBar = el[0].getElementsByClassName('progress-bar')[0];
                    var progressBarWidth = progressBar.getAttribute('aria-valuenow');
                    progressBar.style.width = progressBarWidth + "%";
                }, 0);
            }
          }
    });

  angular
    .module('crowdsource.requester.services', []);

})();