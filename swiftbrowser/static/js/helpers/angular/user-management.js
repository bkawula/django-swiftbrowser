/*
  This angular module faciltates user management in user_management.html which
  is imported by settings.html. It is currently commented out until domains
  are implemented.

  This code is only applicable to keystone users who are admins. Right now
  without domains, anyone with admin access can create and edit users of
  any tenant. With domains, we can restrict admin access to a tenant or a group
  of tenants.
*/
var app = angular.module('userManagement', ['messages']);

app.controller('UserManagementCtrl', function ($scope, $http, users, MessagesHandler) {

  //This function is called after angular.element is finished.
  $scope.users = users.users; /* User data */
  $scope.createUserFormData = {}; /* Holder for form data. */
  $scope.selectedUser = {}; /* Holder data for selected user. */

   /*
    This is the form handler for creating a new user. Submit a post to the
    server to create a user. On success, repopulate the users object to
    show the newly created user.
   */
  $scope.createUser = function () {

    /* Submit the post to the server to create the user. */
    $http({
      method  : 'POST',
      url     : '/create_user/',
      data    : $.param($scope.createUserFormData),  // pass in data as strings
      headers : { 'Content-Type': 'application/x-www-form-urlencoded' }
    })

    /* On success, send success message to the user and update the user data. */
    .success(function (data) {
      if (data.success) {
        MessagesHandler.newSuccessMessage(data.success);
        $http.get('/get_users').then(
          function (response) {
            $scope.users = response.data.users;
          });
      } else {
        MessagesHandler.newErrorMessage(data.error);
      }
    })
    .error(function (data, status, headers, config) {
      $("html").html(data);
    });
  };

  /*
    Given a user object, set the given user as the selected User and display
    the delete user modal
  */
  $scope.openDeleteUser = function (user) {
    $scope.selectedUser = user;
    $('#delete-user').foundation('reveal', 'open');
  };

  /*
    Handle the delete user form. Submit a post to the server to delete the user.
    Reset the selectedUser and repopulate the users object to reflect the
    deleted user.
  */
  $scope.deleteUser = function () {

    /* Submit a post to the server to delete the user. */
    $http({
      method  : 'POST',
      url     : '/delete_user/',
      data    : $.param({
        'user_id': $scope.selectedUser.id}),  // pass in data as strings
      headers : { 'Content-Type': 'application/x-www-form-urlencoded' }
    })
    .success(function (data) {
      if (data.success) {
        MessagesHandler.newSuccessMessage(data.success);

        //On success, update the user list
        $http.get('/get_users').then(
          function (response) {
            $scope.users = response.data.users;
          });
      } else {
        MessagesHandler.newErrorMessage(data.error);
      }
    })
    .error(function (data, status, headers, config) {
      MessagesHandler.newErrorMessage(data);
    });

    //Clear the delete_user input and close the modal
    $scope.confirm_delete_user = "";
    $('#delete-user').foundation('reveal', 'close');
  };

  /*
    Close the delete form.
  */
  $scope.closeDeleteForm = function () {
    $scope.confirm_delete_user = "";
    $('#delete-user').foundation('reveal', 'close');
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

/*
  This is the entry point for the page. We start by calling the
  user_manage_init function to load the inital data.
*/
angular.element(document).ready(user_management_init);
