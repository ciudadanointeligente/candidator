$(document).ready(function() {
        /* Barra fija */

    var updateHeight = function() {
        var extraHeight = 130;
        $(".candidate-edit-menu").height($(".fondo_wizard").height() + 80);
    }
    if ($(".candidate-edit-menu")) {
        $(window).resize(updateHeight);
        updateHeight();
    }
    $('.errorlist li').effect('highlight', 3000);
})
