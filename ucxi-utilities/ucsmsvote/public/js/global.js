$('a[href^=/]').live('click', function(){
    console.log($(this).attr('href'));
    
    $('#main').load($(this).attr('href'));
    return false;
});


function ajaxResponse (response) {
    
    var msg = $('<h4>').addClass('notice');
    if (response.status == 'ok') {
		msg.html('Action completed successfully!').addClass('alert_success');		
    } else {
        msg.html(response.status).addClass('alert_error');
    }
    $('#main').prepend(msg);
    
}

function deletePoll (shortname) {
    $.ajax('/poll/'+shortname, {
        dataType: 'json', type: 'DELETE', success: function(data, textStatus, jqXHR){
            $('.poll-'+shortname).parents('tr').fadeOut();
        }
    });
}
