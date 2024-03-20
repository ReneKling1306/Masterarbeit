document.addEventListener("DOMContentLoaded", function() {
    $("[data-trigger]").on("click", function () {
        var trigger_id = $(this).attr("data-trigger");
        $(trigger_id).toggleClass("show");
        $("body").toggleClass("offcanvas-active");
        $(".line").hide();
        $("#license_upload").hide();
        $("#image_upload").hide();
      });
  
      // close button
      $(".btn-close").click(function (e) {
        $(".navbar-collapse").removeClass("show");
        $("body").removeClass("offcanvas-active");
        $(".line").show();
        $("#license_upload").show();
        $("#image_upload").show();
      });
  
      $(window).resize(function () {
        $(".navbar-collapse").removeClass("show");
        $(".line").show();
        $("#license_upload").show();
        $("#image_upload").show();
      });
})