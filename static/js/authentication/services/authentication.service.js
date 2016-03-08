/**
* Authentication
* @namespace crowdsource.authentication.services
*/
(function () {
  'use strict';

  angular
    .module('crowdsource.authentication.services')
    .factory('Authentication', Authentication);

  Authentication.$inject = ['$cookies', '$http', '$q', '$window'];

  /**
  * @namespace Authentication
  * @returns {Factory}
  */

  function Authentication($cookies, $http, $q, $window) {
    /**
    * @name Authentication
    * @desc The Factory to be returned
    */
    var Authentication = {
      getAuthenticatedAccount: getAuthenticatedAccount,
      isAuthenticated: isAuthenticated,
      login: login,
      logout: logout,
      register: register,
      setAuthenticatedAccount: setAuthenticatedAccount,
      unauthenticate: unauthenticate,
      getOauth2Token: getOauth2Token,
      getCookieOauth2Tokens: getCookieOauth2Tokens,
      attachHeaderTokens: attachHeaderTokens,
      setOauth2Token: setOauth2Token,
      getRefreshToken: getRefreshToken,
      changePassword: changePassword,
      activate_account: activateAccount,
      sendForgotPasswordRequest: sendForgotPasswordRequest,
      resetPassword: resetPassword,
      ignorePasswordReset: ignorePasswordReset
    };

    return Authentication;

    ////////////////////

    /**
    * @name register
    * @desc Try to register a new user
    * @param {string} email The email entered by the user
    * @param {string} password The password entered by the user
    * @param {string} username The username entered by the user
    * @returns {Promise}
    * @memberOf crowdsource.authentication.services.Authentication
    */
    function register(email, firstname, lastname, password1, password2) {
      return $http({
        url: '/api/user/',
        method: 'POST',
        data: {
          email: email,
          first_name: firstname,
          last_name: lastname,
          password1: password1,
          password2: password2
        }
      });
    }

    /**
     * @name login
     * @desc Try to log in with email `email` and password `password`
     * @param {string} email The email entered by the user
     * @param {string} password The password entered by the user
     * @returns {Promise}
     * @memberOf crowdsource.authentication.services.Authentication
     */
    function login(email, password) {
      return $http.post('/api/auth/login/', {
        username: email, password: password
      });
    }
    /**
     * @name get_oauth2_token
     * @desc Try to get oauth2 token with `username`, `password` and response data of
     * the authentication
     * @param {string} username The username the user
     * @param {string} password The password entered by the user
     * @param {string} grant_type This is a password grant type
     * @param {string} client_id Client id issued by authenticate
     * @param {string} client_secret Client secret
     * @returns {Promise}
     * @memberOf crowdsource.authentication.services.Authentication
     */
    function getOauth2Token(username, password, grant_type, client_id, client_secret) {
      return $http.post('/api/oauth2-ng/token', {
        username: username, password: password,
          grant_type: grant_type, client_id:client_id,
          client_secret: client_secret
      });
    }
    /**
     * @name logout
     * @desc Try to log the user out
     * @returns {Promise}
     * @memberOf crowdsource.authentication.services.Authentication
     */
    function logout() {
      return $http.post('/api/auth/logout/')
        .then(logoutSuccessFn, logoutErrorFn);

      /**
       * @name logoutSuccessFn
       * @desc Unauthenticate and redirect to index with page reload
       */
      function logoutSuccessFn(data, status, headers, config) {
        Authentication.unauthenticate();

        $window.location = '/';
      }

      /**
       * @name logoutErrorFn
       * @desc Log "Epic failure!" to the console
       */
      function logoutErrorFn(data, status, headers, config) {
        console.error('Epic failure!');
      }
    }

    /**
     * @name getAuthenticatedAccount
     * @desc Return the currently authenticated account
     * @returns {object|undefined} Account if authenticated, else `undefined`
     * @memberOf crowdsource.authentication.services.Authentication
     */
    function getAuthenticatedAccount() {
      if (!$cookies.get('authenticatedAccount')) {
        return;
      }

      return JSON.parse($cookies.get('authenticatedAccount'));
    }

    /**
     * @name isAuthenticated
     * @desc Check if the current user is authenticated
     * @returns {boolean} True is user is authenticated, else false.
     * @memberOf crowdsource.authentication.services.Authentication
     */
    function isAuthenticated() {
      return !!$cookies.get('authenticatedAccount');
    }

    /**
     * @name setAuthenticatedAccount
     * @desc Stringify the account object and store it in a cookie
     * @param {Object} user The account object to be stored
     * @returns {undefined}
     * @memberOf crowdsource.authentication.services.Authentication
     */
    function setAuthenticatedAccount(account) {
      $http.get('/api/profile/' + account.username + '/')
      .success(function (data, status, headers, config) {
        account.profile = data;
        $cookies.put('authenticatedAccount', JSON.stringify(account));
      }).error(function (data, status, headers, config) {
        console.error('Could not set profile data');
        $cookies.put('authenticatedAccount', JSON.stringify(account));
      });
    }

    /**
     * @name setOauth2Token
     * @desc Stringify the oauth2_response object and store it in a cookie
     * @param {Object} oauth2_response The account object to be stored
     * @returns {undefined}
     * @memberOf crowdsource.authentication.services.Authentication
     */
    function setOauth2Token(oauth2_response) {
      $cookies.put('oauth2Tokens', JSON.stringify(oauth2_response));
    }


    /**
     * Gets oauth2 tokens from cookie.
     * @return {Object} Object containing oauth2 tokens.
     */
    function getCookieOauth2Tokens() {
      return JSON.parse($cookies.get('oauth2Tokens'));
    }

    /**
     * Attaches header tokens to request settings.
     */
    function attachHeaderTokens(settings) {
      var tokens = getCookieOauth2Tokens();
      settings.headers = {
        'Authorization': tokens.token_type + ' ' + tokens.access_token
      };
      return settings;
    }

    /**
     * @name unauthenticate
     * @desc Delete the cookie where the user object is stored
     * @returns {undefined}
     * @memberOf crowdsource.authentication.services.Authentication
     */
    function unauthenticate() {
      $cookies.remove('authenticatedAccount');
      $cookies.remove('oauth2Tokens');
    }

    /**
     * Gets the refresh token and attempts to reset state to authenticated.
     */
    function getRefreshToken() {
      var account = getAuthenticatedAccount();
      var currentTokens = getCookieOauth2Tokens();

      return $http.post('/api/oauth2-ng/token', {
        grant_type: 'refresh_token',
        client_id:account.client_id,
        client_secret: account.client_secret,
        refresh_token: currentTokens.refresh_token
      });
    }
    function changePassword(oldPassword, newPassword, newPassword2){
      return $http({
        url: '/api/user/'+getAuthenticatedAccount().username+'/change_password/',
        method: 'POST',
        data: {
          password: oldPassword,
          password1: newPassword,
          password2: newPassword2   //no need to transfer this but for now required
        }
      });
    }
    function activateAccount(activation_key){
      return $http({
        url: '/api/user/activate_account/',
        method: 'POST',
        data: {
          activation_key: activation_key
        }
      });
    }
    function sendForgotPasswordRequest(email){
      return $http({
        url: '/api/user/forgot_password/',
        method: 'POST',
        data: {
          email: email
        }
      });
    }
    function resetPassword(reset_key, email, password){
      return $http({
        url: '/api/user/reset_password/',
        method: 'POST',
        data: {
          reset_key: reset_key,
          email: email,
          password: password
        }
      });
    }
    function ignorePasswordReset(reset_key){
      return $http({
        url: '/api/user/ignore_password_reset/',
        method: 'POST',
        data: {
          reset_key: reset_key
        }
      });
    }
  }
})();