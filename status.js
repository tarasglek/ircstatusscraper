/*
 * TODO: title should have number of statuses shown...should update this every 5min...should highlight entries tha changed recently
 */
function age(timestamp) {
  var diff_s = (new Date() - timestamp)/1000
  if (diff_s < 60)
    return Math.round(diff_s) + " seconds"
  var diff_m = diff_s / 60;
  if (diff_m < 120)
    return Math.round(diff_m) + " minutes"
  var diff_h = diff_m / 60;
  if (diff_h < 24)
    return Math.round(diff_h) + " hours"
  var diff_d = diff_h / 24;
  return Math.round(diff_d) + " days"
}

function linkify(str) {
  str = str.replace(/(https?:\/\/[^ ]+)/, "<a href='$1' target='_blank'>$1</a>");
  return str.replace(/(bug)\s*([1-9]\d+)/i, "<a href='https://bugzilla.mozilla.org/show_bug.cgi?id=$2' target='_blank'>$1 $2</a>");
}


function got_week(data) {
  var body = $("body")
  var nicks = JSON.parse(data)
  var table = $("<table/>")

  for (var nick in nicks) {
    $("<tr><td><nick>"+nick+"</nick></td></tr>").appendTo(table)
    var ls = nicks[nick]
    var tr = $("<tr/>")
    var tdleft = $("<td/>")
    var tdright = $("<td/>")
    table.append(tr)
    tr.append(tdleft, tdright)

    for (var i = ls.length - 1;i>=0;i--) {
      var status = ls[i];
      $("<div>"+age(status[0]*1000)+"</div>").appendTo(tdleft)
      $("<div>* " +linkify(status[1])+ "</div>").appendTo(tdright)
    }
    $("<tr><td></td></tr>").appendTo(table)
  }
  body.append(table)
  $.ajax({url: "nicks.json"}).done(nickify)
}

function nickify(data) {
  var dict = JSON.parse(data);
  $("nick").each(function () {
                   var e = $(this)
                   var nick = e.text()
                   var weekly_update = nick
                   if (dict[nick]) {
                     if(dict[nick]["weekly-updates"])
                       weekly_update = dict[nick]["weekly-updates"]
                   }
                   var str = "<strong>"+nick+"</strong>: <a href='http://benjamin.smedbergs.us/weekly-updates.fcgi/user/"+weekly_update+"' target='_blank'>weekly-status</a>";
                   e.replaceWith($(str))
                 })
}

$.ajax({url: "data/weeks.json"}).done(function ( data )
               {
                 var weeks = JSON.parse(data);
                 console.log(weeks)
                 for (var i in weeks) {
                   console.log(weeks[i])
                   var fname = "data/" + weeks[i]+".json"
                   $.ajax({url: fname}).done(got_week);
                 }
               });
