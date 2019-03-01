// the remark global is created by the index.html.head.script remark.js reference
/* global remark document */

require('../css/slides_interlignes.css')

// loads the markdown content and starts the slideshow
document.getElementById('source').innerHTML = require('../interlignes.md')
// document.getElementById('source').innerHTML = require('./20181115-16-icoda_thomas.md')

slideshow = remark.create({
  // see https://github.com/gnab/remark/wiki/Configuration
  highlightLines: true
})

slideshow.on('showSlide', function (slide) {
  console.log(slide);
  if (slide.properties.name == 'preprocessing') {
    set_param("display_mode", 0);

  }
  // Slide is the slide being navigated to
});

function set_param(param, value) {
  var url = "http://localhost:8888/param"
  $.ajax({
    type: "POST",
    url: url + "/" + param + "/" +  value,
    data: JSON.stringify({ n: Math.round(value) }),
    contentType: "application/json; charset=utf-8",
    dataType: "json",
    success: function (data) { console.log(data); },
    failure: function (errMsg) { alert(errMsg); }
  });
}




MathJax.Hub.Config({
  tex2jax: {
    skipTags: ['script', 'noscript', 'style', 'textarea', 'pre'],
    inlineMath: [['$', '$'], ["\\(", "\\)"]],
    displayMath: [['$$', '$$'], ["\\[", "\\]"]],
    processEscapes: true
  }
})

MathJax.Hub.Configured()