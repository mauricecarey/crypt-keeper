/**
 * Created by mcarey on 2/13/17.
 */
$(document).ready( function () {
    var active = window.location.pathname;
    $(".nav a[href|='" + active + "']").parent().addClass("active").siblings().removeClass("active");
});
