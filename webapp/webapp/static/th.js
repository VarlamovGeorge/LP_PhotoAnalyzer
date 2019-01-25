$(function() {
  $('a#upd').bind('click', function() {
    $.getJSON($SCRIPT_ROOT + '/settings/update_threshold', {
      threshold: $('input[id="formControlRange"]').val(),
    }, function(data) {
      if ( String(data.result)=="error" ){
        $("#result").text("Ошибка получения данных из БД");
      } else {
        $("#result").text(data.result);
      };
    });
    return false;
  });
});