var app = angular.module('user-management', []);

app.controller('UserManagementCtrl', function ($scope, users) {

  //This function is called after angular.element is finished.
  $scope.users = users.users;
  console.log(users.users);
})

  //Event for when last row in object table has been rendered.
  .directive('onLastRepeat', function () {
    return function (scope, element, attrs) {
      if (scope.$last) {
        setTimeout(function () {
          scope.$emit('onRepeatLast', element, attrs);
        }, 1);
      }
    };
  })

  .directive('ngUpdateHidden', function () {
    return function (scope, el, attr) {
      var model = attr['ngModel'];
      scope.$watch(model, function (nv) {
        el.val(nv);
      });
    };
  });

/* Init of angular*/
angular.element(document).ready(user_management_init);


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
      angular.bootstrap(document, ['user-management']);
    }
  );
}