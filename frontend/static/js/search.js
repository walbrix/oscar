$(document).ready(function () {
  $("div.info").load("./info")

  $("input[name=q]").focus();

  var xhr, previousSearch;

  $("input[name=q]").keyup(function() {
    var q = $("input[name=q]").val();
    if (q == previousSearch) return;
    if (xhr && xhr.readyState != 4) {
      xhr.abort();
    }
    if (q != "") {
      $(".search-in-progress").show();
      xhr = $.ajax({
        url:"./search?q=" + encodeURIComponent(q), 
        success: function(data) { $("#search-results").html(data); },
	error: function(xhr,status,error) { if (status != "abort") {$("#search-results").html("検索エラー");} },
        complete: function() { $(".search-in-progress").hide(); }
      });
    } else {
      $("#search-results").html("");
    }
    previousSearch = q;
  });;
});
