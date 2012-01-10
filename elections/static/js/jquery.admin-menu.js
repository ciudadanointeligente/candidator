$(document).ready(function() {
    if ($(".candidate-edit-menu")) {
        $(window).resize(function() {
        $(".candidate-edit-menu").height($(".fondo_wizard").height());
        });
        $(".candidate-edit-menu").height($(".fondo_wizard").height());
    }
    $('.errorlist li').effect('highlight', 3000);
})
