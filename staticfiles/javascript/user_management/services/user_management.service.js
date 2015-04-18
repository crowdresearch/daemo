
(function () {
  'use strict';

  angular
    .module('crowdresearch.user_management.services')
    .factory('UserManagement', UserManagement);

  UserManagement.$inject = ['$cookies', '$http','$location','$window'];


  function UserManagement($cookies, $http,$location, $window) {
    var UserManagement = {
        register: register,
        login: login,
        profile: profile,
        forgot_password: forgot_password,
        reset_password: reset_password
        //account_activation: account_acctivation
    };

    return UserManagement;

        function login(lc){

            return $http({
              url: '/login/',
              method: 'POST',
              data: {
                username: lc.username,
                password: lc.password
              }
            }).success(function(data, status, headers, config){
                   //redirect to home
                    $window.location.href = '/users/'+data.username;
             })
            .error(function(data, status, headers, config){ $('#login__errors').html(data.message);});
        }
        function register(rc) {
            return $http({
              url: '/register/',
              method: 'POST',
              data: {
                first_name: rc.first_name,
                last_name: rc.last_name,
                email: rc.email,
                password1: rc.password1,
                password2: rc.password2
              }
            }).success(function(data, status, headers, config){
                   //redirect to home
                //temporary
                $window.location.href = '/login/';
             })
            .error(function(data, status, headers, config){ $('#register__errors').html(data.message);});;
        }

        function profile(username){
          return $http.get('/users/', {
              username: username
          });
        }

      function forgot_password(fpc){
          return $http({
              url: '/forgot-password/',
              method: 'POST',
              data: {
                email: fpc.email              }
            }).success(function(data, status, headers, config){
                   //redirect to email sent page
                    $('#forgot_password__errors').html('Email sent.');//not an error
             })
            .error(function(data, status, headers, config){ $('#forgot_password__errors').html(data.message);});
      }

      function reset_password(rpc){
          return $http({
              url: '/reset-password/',//url must be /reset-password/reset_key/{0,1}
              method: 'POST',
              data: {
                password1: rpc.password1,
                password2: rpc.password2
              }
            }).success(function(data, status, headers, config){
                   //redirect to email sent page
                    $('#reset_password__errors').html('Password reset.');//not an error
             })
            .error(function(data, status, headers, config){ $('#reset_password__errors').html(data.message);});
      }
  }
})();