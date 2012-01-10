function toggle_accordion(){
    $("div.menuedit_accordion").toggle('slow');
    return false;
}

$(document).ready(function(){
    $("div.menuedit_accordion").hide();
    $("div.menuedit.link_otras_elecciones a").click(toggle_accordion);
});