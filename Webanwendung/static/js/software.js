$(document).ready(function () {
    $('#download_Windows').click(function (event) {
        handleDownload('windows');
    });
    $('#download_Linux').click(function (event) {
        handleDownload('linux');
    });
    $('#download_macOS').click(function (event) {
        handleDownload('macOS');
    });
    function handleDownload(os) {
        $("#downloadForm").attr("action", "/software/" + os);
        $("#downloadForm").submit();
      }
});