var clear = function () {
  $('.nag').nag('hide');
};
$('.ui.nav.sidebar').sidebar('attach events', '.ui.top.menu > .hamburger.item');

$('.dropdown').dropdown();
$('.nag').nag('show');
$('.close.icon').click(clear);
$(document).ready(function () {
  setTimeout(clear, 5000);
});
$('.ui.sticky')
  .sticky({
    context: '.main-page'
  })
;
