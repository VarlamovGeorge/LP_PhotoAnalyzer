$(function() {
  $('button#calculate').bind('click', function() {
    $.getJSON($SCRIPT_ROOT + '/search', {
      cats: $('input[id="defaultCheck1"]').prop('checked'),
      dogs: $('input[id="defaultCheck2"]').prop('checked'),
      humans: $('input[id="defaultCheck3"]').prop('checked'),
      cars: $('input[id="defaultCheck4"]').prop('checked'),
      cities: $('input[id="defaultCheck5"]').prop('checked'),
      landscapes: $('input[id="defaultCheck6"]').prop('checked'),
      food: $('input[id="defaultCheck7"]').prop('checked'),
      documents: $('input[id="defaultCheck8"]').prop('checked'),
      other: $('input[id="defaultCheck9"]').prop('checked'),
      start_date: $('input[id="start_date"]').val(),
      end_date: $('input[id="end_date"]').val()
    }, function(data) {
      if ( String(data.result)=="error" ){
        $("#error").text("Ошибка получения данных из БД. Возможно не задан порог отнесения к классу (см. Настройки)");
      } else {
        $("#result").text(data.result);
        $('#scroll-group').html(data.result);
        $("#scroll-group").show();
      };
    });
    return false;
  });
});