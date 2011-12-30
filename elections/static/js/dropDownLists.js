$(document).ready(function(){

    // The select element to be replaced:
    var selects = $('select[name="firstCandidate"],select[name="secondCandidate"]');


    // Looping though the options of the original select element
    selects.each(function(index,element){
    var select = $(element);
    var selectBoxContainer = $('<div>',{
        width       : select.outerWidth(),
        'class'     : 'tzSelect',
        html        : '<div class="selectBox"></div>'
    });

    var dropDown = $('<ul>',{'class':'dropDown'});
    var selectBox = selectBoxContainer.find('.selectBox');
    select.find('option').each(function(i){
        var option = $(this);

        if(option.attr('selected')){
            selectBox.html(option.text());
        }

        // As of jQuery 1.4.3 we can access HTML5
        // data attributes with the data() method.

        if(option.data('skip')){
            return true;
        }

        // Creating a dropdown item according to the
        // data-icon and data-html-text HTML5 attributes:

        var li = $('<li>',{
            html:   '<img src="'+option.data('icon')+'" /><span>'+
                    option.data('html-text')+'</span>'
        });

        li.click(function(){

            selectBox.html(option.text());
            dropDown.trigger('hide');

            // When a click occurs, we are also reflecting
            // the change on the original select element:
            select.val(option.val());
            select.trigger('change');

            return false;
        });
        li.attr("id", option.val());
        dropDown.append(li);
    });

    selectBoxContainer.append(dropDown.hide());
    select.hide().after(selectBoxContainer);

    // Binding custom show and hide events on the dropDown:

    dropDown.bind('show',function(){

        if(dropDown.is(':animated')){
            return false;
        }

        selectBox.addClass('expanded');
        dropDown.slideDown();

    }).bind('hide',function(){

        if(dropDown.is(':animated')){
            return false;
        }

        selectBox.removeClass('expanded');
        dropDown.slideUp();

    }).bind('toggle',function(){
        if(selectBox.hasClass('expanded')){
            dropDown.trigger('hide');
        }
        else dropDown.trigger('show');
    });

    selectBox.click(function(){
        dropDown.trigger('toggle');
        return false;
    });
    // If we click anywhere on the page, while the
    // dropdown is shown, it is going to be hidden:
    $(document).click(function(){
        dropDown.trigger('hide');
    });
    });
});