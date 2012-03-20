function toggle_accordion(){
	var is_visible = $("div.menuedit_eleccion").is(':visible');
	if (is_visible) {
		$("div.menuedit_eleccion").hide('blind');
	}
	else {
		$(this).next().show('blind');
	}
    
    

    return false;
}

$(document).ready(function(){
    $("div.menuedit_eleccion").hide();
    $("div.menuedit_eleccion.actual").show();
    $("div.menuedit_tit.nombre").click(toggle_accordion);
    $("div.menuedit_tit.nombre").css('cursor', 'pointer');
});