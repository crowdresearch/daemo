/**
* Authentication
* @namespace crowdsource.authentication.services
*/
(function () {
  'use strict';

  angular
    .module('crowdsource.authentication.services')
    .factory('Authentication', Authentication);

  Authentication.$inject = ['$cookies', '$http', '$q', '$location'];

  /**
  * @namespace Authentication
  * @returns {Factory}
  */

  function Authentication($cookies, $http, $q, $location) {
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
      setOauth2Token: setOauth2Token
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
      return $http.post('/api/user/authenticate/', {
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
      return $http.post('/api/v1/auth/logout/')
        .then(logoutSuccessFn, logoutErrorFn);

      /**
       * @name logoutSuccessFn
       * @desc Unauthenticate and redirect to index with page reload
       */
      function logoutSuccessFn(data, status, headers, config) {
        Authentication.unauthenticate();

        window.location = '/';
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
      if (!$cookies.authenticatedAccount) {
        return;
      }

      return JSON.parse($cookies.authenticatedAccount);
    }
   
    /**
     * @name isAuthenticated
     * @desc Check if the current user is authenticated
     * @returns {boolean} True is user is authenticated, else false.
     * @memberOf crowdsource.authentication.services.Authentication
     */
    function isAuthenticated() {
      return !!$cookies.authenticatedAccount;
    }
   
    /**
     * @name setAuthenticatedAccount
     * @desc Stringify the account object and store it in a cookie
     * @param {Object} user The account object to be stored
     * @returns {undefined}
     * @memberOf crowdsource.authentication.services.Authentication
     */
    function setAuthenticatedAccount(account) {
      $cookies.authenticatedAccount = JSON.stringify(account);
    }

    /**
     * @name setOauth2Token
     * @desc Stringify the oauth2_response object and store it in a cookie
     * @param {Object} oauth2_response The account object to be stored
     * @returns {undefined}
     * @memberOf crowdsource.authentication.services.Authentication
     */
    function setOauth2Token(oauth2_response) {
      $cookies.oauth2Tokens = JSON.stringify(oauth2_response);
    }

    /**
     * @name unauthenticate
     * @desc Delete the cookie where the user object is stored
     * @returns {undefined}
     * @memberOf crowdsource.authentication.services.Authentication
     */
    function unauthenticate() {
      delete $cookies.authenticatedAccount;
    }
  }
})();