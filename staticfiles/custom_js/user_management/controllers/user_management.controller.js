/**
 * Created by dmorina on 16/04/15.
 */
(function () {
  'use strict';

  angular
    .module('crowdresearch.user_management.controllers')
    .controller('LoginController', LoginController)
    LoginController.$inject = ['$location', '$scope', '$routeParams', 'UserManagement'];
  angular
    .module('crowdresearch.user_management.controllers')
    .controller('RegisterController', RegisterController)
    RegisterController.$inject = ['$location', '$scope', '$routeParams', 'UserManagement'];
  angular
    .module('crowdresearch.user_management.controllers')
    .controller('ForgotPasswordController', ForgotPasswordController)
    ForgotPasswordController.$inject = ['$location', '$scope', '$routeParams', 'UserManagement'];
  angular
    .module('crowdresearch.user_management.controllers')
    .controller('ResetPasswordController', ResetPasswordController)
    ResetPasswordController.$inject = ['$location', '$scope', '$routeParams', 'UserManagement'];

    function LoginController($location, $scope, $routeParams, UserManagement) {
        $scope.$on('$routeChangeSuccess', function() {
            //to be used later to get the url parameters like "next"
        });
        this.login = login;
        function login() {
            UserManagement.login(this);
        }
    }
    function RegisterController($location, $scope, $routeParams, UserManagement) {
        $scope.$on('$routeChangeSuccess', function() {
            //to be used later to get the url parameters like "next"
        });
        this.register = register;
        function register() {
            UserManagement.register(this);
        }
    }
    function ForgotPasswordController($location, $scope, $routeParams, UserManagement) {
        $scope.$on('$routeChangeSuccess', function() {
        });
        this.forgot_password = forgot_password;
        function forgot_password() {
            UserManagement.forgot_password(this);
        }
    }
    function ResetPasswordController($location, $scope, $routeParams, UserManagement) {
        $scope.$on('$routeChangeSuccess', function() {
        });
        this.reset_password = reset_password;
        function reset_password() {
            UserManagement.reset_password(this);
        }
    }

})();