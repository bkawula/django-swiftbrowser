/*
  This angular model is used in several places to receive error and success
  messages. It uses a factory to allow other angular controllers to send
  messages that this module controls.
*/
angular.module('messages', [])

  .factory('MessagesHandler', function ($rootScope) {

    var messageHandler = {};

    /* The message to be displayed. */
    messageHandler.message = '';

    /* The following functions are called by other controllers. They send a
    broadcast that is picked up by the MessagesCtrl which displays error and
    success messages. */

    messageHandler.newErrorMessage = function (message) {
      this.message = message;
      $rootScope.$broadcast('newMessageErrorAvailable');
    };

    messageHandler.newSuccessMessage = function (message) {
      this.message = message;
      $rootScope.$broadcast('newMessageSuccessAvailable');
    };

    return messageHandler;
  })

  /* The Messages controller that displays and hides error and success
  messages. */
  .controller('MessagesCtrl', ['$scope', 'MessagesHandler', function ($scope, MessagesHandler) {

    $scope.displayError = false;
    $scope.displaySuccess = false;

    $scope.errorMessage = 'error';
    $scope.successMessage = '';

    /*
      Triggered when a newMessageErrorAvailable is broadcasted, updates the
      error message and displays it.
    */
    $scope.$on('newMessageErrorAvailable', function () {
      $scope.errorMessage = MessagesHandler.message;
      $scope.displayError = true;
      $scope.$applyAsync();
    });

    /*
      Triggered when a newMessageSuccessAvailable is broadcasted, updates the
      success message and displays it.
    */
    $scope.$on('newMessageSuccessAvailable', function () {
      $scope.successMessage = MessagesHandler.message;
      $scope.displaySuccess = true;
      $scope.$applyAsync();
    });

    /*
      The following functions are trigger in messages.html when the user
      dismisses the error or success messages.
    */

    $scope.errorOff = function () {
      $scope.displayError = false;
      $scope.errorMessage = '';
    };

    $scope.successOff = function () {
      $scope.displaySuccess = false;
      $scope.successMessage = '';
    };

  }]);

