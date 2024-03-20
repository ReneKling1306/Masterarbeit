document.addEventListener("DOMContentLoaded", function() {
  $("#default_next").on("click", function () {
      $("#default").removeClass("active");
      $("#default_step").removeClass("active");
      if ($("#radio_yes").is(":checked")) {
        $("#add_info").addClass("active");
        $("#add_info_step").addClass("active");
        $("#add_info").addClass("default");
        if ($(".card").outerWidth() >= 500) {
          $(".right-side").show();
        }
        license = $("#license-select").val();
        var link = '<a href="/licenses/' + license.replace(/\s+/g, '-').toLowerCase() + '" style="color: black;">' + license + '</a>'
        $("#selected").html(link);
        if (license.startsWith("BY")) {
          $("#add_info_next").prop("disabled", true);
          $("#creator")
            .add($("#email"))
            .add($("#contact"))
            .on("input", function () {
              if (
                $("#creator").val().trim() === "" &&
                $("#email").val().trim() === "" &&
                $("#contact").val().trim() === ""
              ) {
                $("#add_info_next").prop("disabled", true); 
              } else {
                $("#add_info_next").prop("disabled", false); 
              }
            });
        } else {
          $("#add_info_next").prop("disabled", false);
        }
      } else {
        license = "";
        $("#allow").addClass("active");
        $("#allow_step").addClass("active");
      }
    });
  
    $("#add_info_next").on("click", function () {
      $("#add_info").removeClass("active");
      $("#add_info_step").removeClass("active");
      $("#accept_terms").addClass("active");
      $("#accept_terms_step").addClass("active");
      var creators = $("#creator").val();
      var email = $("#email").val();
      var contact = $("#contact").val();
      var udd = $("#UDD").val();
      function maxLength(text) {
        return text.length > 50 ? text.slice(0, 50) + "..." : text;
      }
      if ($("#creator").val()) {
        $("#display").html(`Creator(s):<br>${maxLength(creators)}<hr class="line" />`);
      }
      if ($("#email").val()) {
        $("#display").append(`Email:<br>${maxLength(email)}<hr class="line" />`);
      }
      if ($("#contact").val()) {
        $("#display").append(`Contact:<br>${maxLength(contact)}<hr class="line" />`);
      }
      if ($("#UDD").val()) {
        $("#display").append(`UDD:<br>${maxLength(udd)}<hr class="line" />`);
      }
    });
  
    $("#accept_terms_next").on("click", function () {
      $("#accept_terms").removeClass("active");
      $("#accept_terms_step").removeClass("active");
      $("#licensing_tool").addClass("active");
      $("#licensing_tool_step").addClass("active");
      $("#downloadButton").show();
      $("#downloadButton_label").show();
    });
  
    $("#allow_next").on("click", function () {
      $("#allow").removeClass("active");
      $("#allow_step").removeClass("active");
      if ($("#radio_allow_no").is(":checked")) {
        $("#add_info").addClass("active");
        $("#add_info_step").addClass("active");
        $("#add_info").addClass("disallow");
        if ($(".card").outerWidth() >= 500) {
          $(".right-side").show();
        }
        license = "Do Not Train";
        $("#selected").html(license);
      } else {
        $("#attribution").addClass("active");
        $("#attribution_step").addClass("active");
      }
    });
  
    $("#attribution_next").on("click", function () {
      $("#attribution").removeClass("active");
      $("#attribution_step").removeClass("active");
      $("#commercial").addClass("active");
      $("#commercial_step").addClass("active");
    });
  
    $("#commercial_next").on("click", function () {
      $("#commercial").removeClass("active");
      $("#commercial_step").removeClass("active");
      $("#generative").addClass("active");
      $("#generative_step").addClass("active");
    });
  
    $("#generative_next").on("click", function () {
      $("#generative").removeClass("active");
      $("#generative_step").removeClass("active");
      $("#add_info").addClass("active");
      $("#add_info_step").addClass("active");
      if ($(".card").outerWidth() >= 500) {
        $(".right-side").show();
      }
      if ($("#radio_attribution_yes").is(":checked")) {
        license = "BY";
        $("#add_info_next").prop("disabled", true);
        $("#creator")
          .add($("#email"))
          .add($("#contact"))
          .on("keyup", function () {
            if (
              $("#creator").val().trim() === "" &&
              $("#email").val().trim() === "" &&
              $("#contact").val().trim() === ""
            ) {
              $("#add_info_next").prop("disabled", true); 
            } else {
              $("#add_info_next").prop("disabled", false); 
            }
          });
      } else {
        $("#add_info_next").prop("disabled", false);
      }
      if ($("#radio_commercial_no").is(":checked")) {
        if (license != "") {
          license += "-";
        }
        license += "NC";
      }
      if ($("#radio_generative_no").is(":checked")) {
        if (license != "") {
          license += "-";
        }
        license += "NG";
      }
      if (license == "") {
        license = "Permitted For Training";
      }
      var link = '<a href="/licenses/' + license.replace(/\s+/g, '-').toLowerCase() + '" style="color: black;">' + license + '</a>'
      $("#selected").html(link);
    });
  
    $("#add_info_back").on("click", function () {
      $("#add_info").removeClass("active");
      $("#add_info_step").removeClass("active");
      $(".right-side").hide();
      if ($("#add_info").hasClass("default")) {
        $("#default").addClass("active");
        $("#default_step").addClass("active");
        $("#add_info").removeClass("default");
      } else if ($("#add_info").hasClass("disallow")) {
        $("#allow").addClass("active");
        $("#allow_step").addClass("active");
        $("#add_info").removeClass("disallow");
      } else {
        $("#generative").addClass("active");
        $("#generative_step").addClass("active");
        $("#selected").html(``);
        license = "";
      }
    });
  
    $("#allow_back").on("click", function () {
      $("#default").addClass("active");
      $("#default_step").addClass("active");
      $("#allow").removeClass("active");
      $("#allow_step").removeClass("active");
    });
  
    $("#attribution_back").on("click", function () {
      $("#allow").addClass("active");
      $("#allow_step").addClass("active");
      $("#attribution").removeClass("active");
      $("#attribution_step").removeClass("active");
    });
  
    $("#commercial_back").on("click", function () {
      $("#attribution").addClass("active");
      $("#attribution_step").addClass("active");
      $("#commercial").removeClass("active");
      $("#commercial_step").removeClass("active");
    });
  
    $("#generative_back").on("click", function () {
      $("#commercial").addClass("active");
      $("#commercial_step").addClass("active");
      $("#generative").removeClass("active");
      $("#generative_step").removeClass("active");
    });
  
    $("#accept_terms_back").on("click", function () {
      $("#add_info").addClass("active");
      $("#add_info_step").addClass("active");
      $("#accept_terms").removeClass("active");
      $("#accept_terms_step").removeClass("active");
      $("#display").html("");
    });
  
    $("#licensing_tool_back").on("click", function () {
      $("#accept_terms").addClass("active");
      $("#accept_terms_step").addClass("active");
      $("#licensing_tool").removeClass("active");
      $("#licensing_tool_step").removeClass("active");
      $("#downloadButton").hide();
      $("#downloadButton_label").hide();
    });
  
    $("#radio_yes").on("change", function () {
      if ($("#radio_yes").is(":checked")) {
        $("#license-selector").show();
        $("#content").hide();
        $("#default_next").prop("disabled", true);
      }
    });
  
    $("#radio_no").on("change", function () {
      if ($("#radio_no").is(":checked")) {
        $("#license-selector").hide();
        $("#license-select").prop("selectedIndex", 0);
        $("#content").show();
        $("#default_next").prop("disabled", false);
      }
    });
  
    $("#license-select").on("change", function () {
      if ($(this).val() == "") {
        $("#default_next").prop("disabled", true);
      } else {
        $("#default_next").prop("disabled", false);
      }
    });
  
    $(".checkbox").on("change", function () {
      if ($(".checkbox:checked").length == $(".checkbox").length) {
        $("#accept_terms_next").prop("disabled", false);
      } else {
        $("#accept_terms_next").prop("disabled", true);
      }
    });
  
    $("[data-trigger]").on("click", function () {
      $(".card").hide();
      $(".btn-close").addClass("open");
    });
  
    $(".btn-close").on("click", function (e) {
      $(".card").show();
      $(".btn-close").removeClass("open");
    });
  
    $('INPUT[type="file"]').on("change", function () {
      var ext = this.value.match(/\.(.+)$/)[1].toLowerCase();
      allowed_extensions = [
        'jpg', 'jpeg', 'jpe', 'png', 'jng', 'mng', 'tiff', 'tif', 'webp', 'jp2', 'jpf', 'jpm',
                      'heif', 'heic', 'hif', 'gif', 'eps', 'psd', 'avif', 'flif', 'mp4'
      ];
      if (allowed_extensions.includes(ext)) {
        $("#uploadButton").prop("disabled", false);
      } else {
        alert(
          '.' +
            ext +
            ' - is not an allowed file type. Currently supported file types are: ' +
            allowed_extensions
        );
        this.value = "";
      }
    });
  
    $(window).on("load", function () {
      if ($("#radio_no").is(":checked")) {
        $("#license-selector").hide();
        $("#content").show();
        $("#default_next").prop("disabled", false);
      }
      if ($("#radio_yes").is(":checked")) {
        $("#license-selector").show();
        $("#default_next").prop("disabled", true);
        $("#license-select").prop("selectedIndex", 0);
      }
      if ($(".card").outerWidth() < 884) {
        $(".left-side").hide();
      } else {
        $(".left-side").show();
        $(".card").show();
      }
    });
  
    $(window).resize(function () {
      if ($(".card").outerWidth() < 884) {
        $(".left-side").hide();
        
      } else {
        $(".left-side").show();
        
        if ($(".btn-close").hasClass("open")) {
          $(".btn-close").click();
        }
      }
      if ($(".card").outerWidth() < 500) {
        $(".right-side").hide();
        $("#downloadButton_middle").show();
        $("#downloadButton_label_middle").show();
      } else {
        if (
          $("#add_info").hasClass("active") ||
          $("#licensing_tool").hasClass("active") ||
          $("#accept_terms").hasClass("active")
        ) {
          $(".right-side").show();
          $("#downloadButton_middle").hide();
        $("#downloadButton_label_middle").hide();
        }
      }
    });
  
    $(document).ready(function () {
      $('input[type="text"]').val('');
      $('input[type="checkbox"]').prop('checked', false);
      $('#uploadButton').prop('disabled', true);
      $('#accept_terms_next').prop('disabled', true);
      $('[data-toggle="tooltip"]').tooltip()
  
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
        var formData = new FormData($("#form")[0]);
  
        var xhr = new XMLHttpRequest();
  
        xhr.upload.addEventListener("progress", function (event) {
          if (event.lengthComputable) {
            var percentComplete = (event.loaded / event.total) * 100;
            document.getElementById("progressBar").value =
              Math.round(percentComplete);
            document.getElementById("status").innerHTML =
              Math.round(percentComplete) + "% uploaded... please wait";
          }
        });
  
        xhr.addEventListener("load", function () {
          if (xhr.status === 200) {
            var jsonResponse = JSON.parse(xhr.responseText);
            if (jsonResponse.hasOwnProperty("error")) {
              alert(jsonResponse.error);
              $("#progress").hide();
              $("#uploadButton").prop('disabled', false);
            } else if (jsonResponse.hasOwnProperty("unique_id")) {
              document.getElementById("progressBar").value = 100;
              document.getElementById("status").innerHTML =
                "Upload finished! Download will now begin.";
              $("#uploadButton").prop('disabled', false);
              var unique_id = jsonResponse.unique_id;
              var single = jsonResponse.single;
              handleDownload(unique_id, single);
            }
          } else {
            document.getElementById("status").innerHTML = "Upload failed";
            $("#uploadButton").prop('disabled', false);
          }
        });
  
        xhr.addEventListener("error", function () {
          console.error("Upload failed");
        });
  
        xhr.open("POST", "/license-picker/upload");
        xhr.send(formData);
      });
  
      function handleDownload(unique_id, single) {
        $("#downloadForm").attr("action", "/download/" + unique_id + "/" + single);
        $("#downloadForm").submit();
      }
    }); 
  
  })