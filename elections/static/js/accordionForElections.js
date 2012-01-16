function toggle_accordion(){
    $("div.menuedit_eleccion").hide('slow');
    $(this).next().show('slow');

    return false;
}

$(document).ready(function(){
    $("div.menuedit_eleccion").hide();
    $("div.menuedit_eleccion.actual").show();
    $("div.menuedit_tit.nombre").click(toggle_accordion);
    $("div.menuedit_tit.nombre").css('cursor', 'pointer');
});