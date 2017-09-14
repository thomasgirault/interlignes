var gui = new dat.GUI();

gui.add({"min_depth":33}, 'min_depth', 0, 255).step(1).onChange( function(value) {
    console.log(value);
    $.ajax({
      type: "POST",
      url: "http://localhost:8888/param/min_depth/" + value,
      data: JSON.stringify({"min_depth": value}),
      contentType: "application/json; charset=utf-8",
      dataType: "json",
      success: function(data){console.log(data);},
      failure: function(errMsg) {
          alert(errMsg);
      }
  });
});

gui.add({"max_depth":40}, 'max_depth', 0, 255).step(1).onChange( function(value) {
    console.log(value);
    $.ajax({
      type: "POST",
      url: "http://localhost:8888/param/max_depth/" + value,
      data: JSON.stringify({"max_depth": value}),
      contentType: "application/json; charset=utf-8",
      dataType: "json",
      success: function(data){console.log(data);},
      failure: function(errMsg) {
          alert(errMsg);
      }
  });
});



gui.add({"theta":10}, 'theta', 0, 255).step(1).onChange( function(value) {
    console.log(value);
    $.ajax({
      type: "POST",
      url: "http://localhost:8888/param/theta/" + value,
      data: JSON.stringify({"theta": value}),
      contentType: "application/json; charset=utf-8",
      dataType: "json",
      success: function(data){console.log(data);},
      failure: function(errMsg) {
          alert(errMsg);
      }
  });
});


gui.add({"save":0}, 'save', 0, 2).step(1).onChange( function(value) {
    console.log(value);
    $.ajax({
      type: "POST",
      url: "http://localhost:8888/param/save/" + value,
      data: JSON.stringify({"save": value}),
      contentType: "application/json; charset=utf-8",
      dataType: "json",
      success: function(data){console.log(data);},
      failure: function(errMsg) {
          alert(errMsg);
      }
  });
});


gui.add({"MAX_DIST":0}, 'MAX_DIST', 0, 18750).step(256).onChange( function(value) {
    console.log(value);
    $.ajax({
      type: "POST",
      url: "http://localhost:8888/param/MAX_DIST/" + value,
      data: JSON.stringify({"MAX_DIST": value}),
      contentType: "application/json; charset=utf-8",
      dataType: "json",
      success: function(data){console.log(data);},
      failure: function(errMsg) {
          alert(errMsg);
      }
  });
});