var app = angular.module('userManagement', ['messages']);

app.controller('UserManagementCtrl', function ($scope, $http, users, MessagesHandler) {

  //This function is called after angular.element is finished.
  $scope.users = users.users; /* User data */
  $scope.formData = {}; /* Holder for form data. */

   //Handler for submiting new user form.
  $scope.createUser = function () {

    //Submit the form
    $http({
      method  : 'POST',
      url     : '/create_user/',
      data    : $.param($scope.formData),  // pass in data as strings
      headers : { 'Content-Type': 'application/x-www-form-urlencoded' }
    })
      .success(function (data) {
        if (data.success) {
          MessagesHandler.newSuccessMessage(data.success);
        } else {
          MessagesHandler.newErrorMessage(data.error);
        }
      })
      .error(function (data) {
        MessagesHandler.newErrorMessage("Error creating user.");
      });
  };
});


/* Added in for CSRF support. */
app.config(function ($httpProvider) {
  $httpProvider.defaults.headers.post['X-CSRFToken'] = $('input[name=csrfmiddlewaretoken]').val();
});

/*
  Initiatialize requests for user management functions.
*/
function user_management_init() {
  var initInjector = angular.injector(['ng']);
  var $http = initInjector.get('$http');
  $http.get('/get_users').then(
    function (response) {

      //Store data in constant called users
      app.constant('users', response.data);

      //Init the controller
      angular.bootstrap(document, ['userManagement']);
    }
  );
}

/* Init of angular*/
angular.element(document).ready(user_management_init);
