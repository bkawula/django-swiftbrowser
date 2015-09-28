angular.module('messages', [])

  .factory('MessagesHandler', function ($rootScope) {

    var messageHandler = {};

    /* The message to be displayed. */
    messageHandler.message = '';

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

  .controller('MessagesCtrl', ['$scope', 'MessagesHandler', function ($scope, MessagesHandler) {

    $scope.displayError = false;
    $scope.displaySuccess = false;

    $scope.errorMessage = 'error';
    $scope.successMessage = '';

    $scope.$on('newMessageErrorAvailable', function () {
      $scope.errorMessage = MessagesHandler.message;
      $scope.displayError = true;
      $scope.$apply();
    });

    $scope.$on('newMessageSuccessAvailable', function () {
      $scope.successMessage = MessagesHandler.message;
      $scope.displaySuccess = true;
      $scope.$apply();
    });

    $scope.errorOff = function () {
      $scope.displayError = false;
      $scope.errorMessage = '';
    };

    $scope.successOff = function () {
      $scope.displaySuccess = false;
      $scope.successMessage = '';
    };

  }]);

