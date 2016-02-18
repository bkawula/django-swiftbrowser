var app = angular.module('object-table', ['messages']);

/*
  Obtain the base url of the application to make calls to the server.
*/
app.config(["$provide", function ($provide) {
  $provide.value("baseurl", $("#baseurl").attr("href"));
}]);

/**
  * Initiate object table data for the controller.
 */
function get_object_table() {
  var initInjector = angular.injector(['ng']);
  var $http = initInjector.get('$http');
  $http.get($("#baseurl").attr("href") + 'get_object_table/').then(
    function (response) {

      //Store data in constant called items
      app.constant('items', response.data.data);

      //Init the controller
      angular.bootstrap(document, ['object-table']);
    }
  );
}

app.controller('ObjectTableCtrl', function ($scope, $http, items, MessagesHandler, baseurl) {

  //This function is called after angular.element is finished.
  $scope.folders = items.folders;
  $scope.objects = items.objects;
  $scope.container = items.container;
  $scope.incomplete_slo = items.incomplete_slo;
  $scope.baseurl = baseurl;

  $scope.$on('onRepeatLast', function () {
    app.applyTableEvents();
  });

  function refreshObjectTable() {
    $http.get(baseurl + 'get_object_table/').then(
      function (response) {
        $scope.folders = response.data.data.folders;
        $scope.objects = response.data.data.objects;
        $scope.incomplete_slo = response.data.data.incomplete_slo;
      }
    );
  }
  $scope.refreshObjectTable = refreshObjectTable;

  // Provide upload_form.js access to internal function
  $scope.$on("refreshObjectTable", function () {
    refreshObjectTable();
  });

  // Provide upload_form.js access to internal function
  $scope.MessagesHandler = MessagesHandler;

  /*
    Make a request to the server to delete the incomplete SLO.
  */
  $scope.delete_incomplete_slo = function (key) {

    //Bind slo delete
    $('#delete-slo-modal').foundation('reveal', 'open', {
        close_on_background_click: false,
    });

    $("#slo-upload a.close-reveal-modal").click(function () {
      location.reload();
    });

    var formData = {
        csrfmiddlewaretoken  : $('input[name=csrfmiddlewaretoken]').val(),
    };

    $.ajax({
        type        : 'POST',
        url     : baseurl + "delete_incomplete_slo/" + $scope.container + "/" + key.name,
        data        : formData,
    })
      .success(function (data) {
        // Update message
        MessagesHandler.newSuccessMessage(data);

        // Refresh table.
        $scope.refreshObjectTable();
        $("#css-progress-wrap").toggle(false);

        $('#delete-slo-modal').foundation('reveal', 'close', {
            close_on_background_click: false,
        });
      })
      .error(function (data) {

        MessagesHandler.newErrorMessage(data);

        $('#delete-slo-modal').foundation('reveal', 'close', {
            close_on_background_click: false,
        });
      });
  };

})

  //Controller for new folder form.
  .controller('CreateFolderCtrl', function ($scope, $http, $rootScope, items, baseurl) {

    $scope.showForm = 1; /* Variable for toggling the form after submission. */
    $scope.showLoader = 0; /* Variable for toggling the loader. */
    $scope.formData = {}; /* Holder for form data. */

    var create_folder_url = baseurl + "create_pseudofolder/" + items.container + "/";

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
      var exp = parseInt(Math.log(size) / Math.log(1024), 10);
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

  /*
  Format filename
    from "folder/name/file.mp4"
    to "file.mp4"
  */
  .filter('formatFileName', function () {
    'use strict';

    return function (string) {
      var split = string.split("/");
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
  $("a.delete-object").off("click");
  $("a.delete-object").on("click", function (e) {
    //Prompt user to confirm.
    /*global confirm: true*/
    if (!confirm("Are you sure you want to delete " + $(this).attr("data-name") + "?")) {
      e.preventDefault();
    }
  });

  /*
      Bind SLO upload button
  */
  $("button.slo-upload-button").click(function () {
      $('#slo-upload').foundation('reveal', 'open', {
          close_on_background_click: false,
      });
  });

};
