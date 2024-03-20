document.addEventListener("DOMContentLoaded", function() {
  $('INPUT[id="image"]').change(function () {
      var files = this.files;
      allowed_extensions = [
        'jpg', 'jpeg', 'jpe', 'png', 'jng', 'mng', 'tiff', 'tif', 'webp', 'jp2', 'jpf', 'jpm',
                      'heif', 'heic', 'hif', 'gif', 'eps', 'psd', 'avif', 'flif', 'mp4'
      ];
      var validFileTypes = true;
      for (var i = 0; i < files.length; i++) {
        var ext =  files[i].name.match(/\.([^.]+)$/);
        if (!ext) {
            alert("Datei hat keine Dateierweiterung.");
            this.value = "";
            validFileTypes = false;
            $("#uploadButton").prop("disabled", true);
            break;
        }
        ext = ext[1];
        if (!allowed_extensions.includes(ext)) {
          alert(
            '".' +
              ext +
              '" - is not an allowed file type. Currently supported file types are: ' +
              allowed_extensions
          );
          this.value = "";
          $("#uploadButton").prop("disabled", true);
          validFileTypes = false;
          break;
        }
      }
      if (validFileTypes) {
        if ($('#license')[0].files[0] !== undefined){
          $("#uploadButton").prop("disabled", false);
        }
      }
      });
      $('INPUT[id="license"]').change(function () {
        var ext = this.value.match(/\.(.+)$/)[1];
        allowed_extensions = [
          "xmp"
        ];
        if (allowed_extensions.includes(ext)) {
          console.log($('#license')[0].files[0])
          if ($('#image')[0].files[0] !== undefined){
            $("#uploadButton").prop("disabled", false);
          }
        } else {
          alert(
            '".' +
              ext +
              '" - is not an allowed file type. You have to upload a valid license.xmp file. You can create one with our License-Picker: '
          );
          this.value = "";
          $("#uploadButton").prop("disabled", true);
        }
      });
      $(document).ready(function () {
        $('#uploadButton').prop('disabled', true);
        var maxFiles = 256;
        var max = 250
        var maxTotalSize = max * 1024 * 1024;
        $('input[type="file"]').on('change', function() {
          var files = $(this)[0].files;
          if (files.length > maxFiles) {
            alert('You have exceeded the data limit of ' + maxFiles + ' files. Please upload your images in multiple steps.');
            $(this).val('');
          }

          var totalSize = 0;
          for (var i = 0; i < files.length; i++) {
            totalSize += files[i].size;
          }

          if (totalSize > maxTotalSize) {
            alert('You have exceeded the data limit of ' + max + ' MB. Please upload your images in multiple steps.');
            $(this).val('');
          }
        });
        $("#uploadButton").click(function (e) {
          e.preventDefault();
          $("#progress").show();
          $("#uploadButton").prop('disabled', true);
          var formData = new FormData($("#image_form")[0]);
          var xhr = new XMLHttpRequest();

          // Progress event handler
          xhr.upload.addEventListener("progress", function (event) {
            if (event.lengthComputable) {
              var percentComplete = (event.loaded / event.total) * 100;
              document.getElementById("progressBar").value =
                Math.round(percentComplete);
              document.getElementById("status").innerHTML =
                Math.round(percentComplete) + "% uploaded... please wait";
            }
          });

          // Load event handler
          xhr.addEventListener("load", function () {
            if (xhr.status === 200) {
              var jsonResponse = JSON.parse(xhr.responseText);
              if (jsonResponse.hasOwnProperty('error')) {
                alert(jsonResponse.error);
                $("#progress").hide();
                $("#uploadButton").prop('disabled', false);
              } else if (jsonResponse.hasOwnProperty('unique_id')){
                document.getElementById("progressBar").value = 100;
                document.getElementById("status").innerHTML = "Upload finished! Download will now begin.";
                $("#uploadButton").prop('disabled', false);
                var unique_id = jsonResponse.unique_id;
                var single = jsonResponse.single;
                handleDownload(unique_id, single);
              }
            } else {
              // Display an error message in the status area
              document.getElementById("status").innerHTML = "Upload failed";
              $("#uploadButton").prop('disabled', false);
            }
          });

          // Error event handler
          xhr.addEventListener("error", function () {
            console.error("Upload failed");
          });

          xhr.open("POST", "/licensing-tool/upload");
          xhr.send(formData);
        });

        function handleDownload(unique_id, single) {
          $("#downloadForm").attr("action", "/download/" + unique_id + "/" + single);
          $("#downloadForm").submit();
        }
      });
})