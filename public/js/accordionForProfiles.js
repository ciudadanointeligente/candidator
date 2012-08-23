function toggle(){
    $(this).next().toggle('slow');
    return false;
}
jQuery(document).ready(function(){
    $('.trayectoria .accordion h3:not(:first), .accordion .category h3:not(:first)').click(
	toggle
    ).next().hide();
    $('.trayectoria .accordion h3:first, .accordion .category h3:first').click(
	toggle
    ).next();
});