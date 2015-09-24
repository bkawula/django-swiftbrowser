var app = angular.module('object-table', []);

/**
  * Initiate object table data for the controller.
 */
function get_object_table() {
  var initInjector = angular.injector(['ng']);
  var $http = initInjector.get('$http');
  $http.get('/get_object_table').then(
    function (response) {

      //Store data in constant called items
      app.constant('items', response.data);

      //Init the controller
      angular.bootstrap(document, ['object-table']);
    }
  );
}

app.controller('ObjectTableCtrl', function ($scope, $http, items) {

  //This function is called after angular.element is finished.
  $scope.folders = items.folders;
  $scope.objects = items.objects;
  $scope.container = items.container;

  $scope.$on('onRepeatLast', function () {
    app.applyTableEvents();
  });

  function refreshObjectTable() {
    $http.get('/get_object_table').then(
      function (response) {
        $scope.folders = response.data.folders;
        console.log(response.data);
      }
    );
  }

  $scope.$on("refreshObjectTable", function () {
    refreshObjectTable();
  });
})

  //Controller for new folder form.
  .controller('CreateFolderCtrl', function ($scope, $http, $rootScope, items) {

    $scope.showForm = 1; /* Variable for toggling the form after submission. */
    $scope.showLoader = 0; /* Variable for toggling the loader. */
    $scope.formData = {}; /* Holder for form data. */
    var create_folder_url = "/create_pseudofolder/" + items.container + "/";

    //Add prefix for new folders that will be in existing folders.
    if (items.folder_prefix) {
      create_folder_url += items.folder_prefix;
    }

    //Handler for submiting new folder form.
    $scope.createFolder = function () {

      //Display loading image
      $scope.showForm = 0;
      $scope.showLoader = 1;

      //Submit the form
      $http({
        method  : 'POST',
        url     : create_folder_url,
        data    : $.param($scope.formData),  // pass in data as strings
        headers : { 'Content-Type': 'application/x-www-form-urlencoded' }  // set the headers so angular passing info as form data (not request payload)
      })
        .success(function () {

          $('#pseudoContainer').foundation('reveal', 'close');
          $rootScope.$broadcast('refreshObjectTable');
          $scope.showForm = 1;
          $scope.showLoader = 0;
          $scope.formData.foldername = "";
        })
        .error(function () {
          //TODO: Display error message
          console.log($scope.formData);
        });
    };
  })

  //Filter to display the file size in a compact way. Ex. 3GB or 100Bytes
  .filter('formatByte', function () {
    'use strict';

    return function (size) {
      var exp = Math.log(size) / Math.log(1024);
      if (exp < 1) {
        exp = 0;
      }
      return (size / Math.pow(1024, exp)).toFixed(1) + ' ' +
        ((exp > 0) ? 'KMGTPEZY'[exp - 1] + 'B' : 'Bytes');
    };
  })

  /*
  Format the pseudo folder:
    from "folder/name/"
    to "name"
  */
  .filter('formatPseudoFolder', function () {
    'use strict';

    return function (string) {

      var stripped = string.substring(0, string.length - 1);
      var split = stripped.split("/");
      return split[split.length - 1];
    };
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
      var model = attr.ngModel;
      scope.$watch(model, function (nv) {
        el.val(nv);
      });
    };
  });

/* Added in for CSRF support. */
app.config(function ($httpProvider) {
  $httpProvider.defaults.headers.post['X-CSRFToken'] = $('input[name=csrfmiddlewaretoken]').val();
});

angular.element(document).ready(get_object_table);

/*
TODO: replace with loader angular logic
    Display the loader in the object table.
*/
function showLoader() {

  $('#objecttable').html(
    '<div id="progress" class="center-progress">' +
      '<div class="loader">Loading...</div>' +
      '</div>'
  );
}

/*
    After a table is loaded, new events need to be applied to the page.
*/
app.applyTableEvents = function () {

  //Re-apply foundation
  $(document).foundation();

  //Reapply dismiss of alert boxes
  $(".alert-box").click(function () {
    $(this).slideUp();
  });

  //Delete object binding.
  $("a.delete-object").on("click", function (e) {
    //Prompt user to confirm.
    /*global confirm: true*/
    if (confirm("Are you sure you want to delete " + $(this).attr("data-name") + "?")) {
      showLoader();
      $("#progress").show();
    } else {
      e.preventDefault();
    }
  });

  //Delete folder binding.
  $("a.delete-folder").on("click", function (e) {

    if (confirm("Are you sure you want to delete " + $(this).attr("data-name") + "?")) {
      if (confirm("This will delete " + $(this).attr("data-name") + " and all it's contents. Are you sure?")) {
        showLoader();
        $("#progress").show();
      } else {
        e.preventDefault();
      }
    } else {
      e.preventDefault();
    }
  });
};
