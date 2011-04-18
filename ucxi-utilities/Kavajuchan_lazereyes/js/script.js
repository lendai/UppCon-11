var $participants = participants;

var _pos = 0;

function change (n) {

	var all = $('#name, #char, #origin, #smscode');
	var _c = $participants[n].cosplay;
	
	all.animate({opacity: 0}, 100, function(){
	
	
		$('#name').html(_c.user.firstname);
		$('#char').html(_c.character);
		$('#origin').html(_c.series);
		$('#smscode').html('UC VOTE '+_c.id);
		all.animate({opacity: 1}, 300);
	});
}
function next () {
	_pos++;
	change(_pos);
}

function prev () {
	_pos--;
	change(_pos < 0 ? (_pos=0) : _pos);
}


$(window).keydown(function(e){
	switch(e.which) {
		case 39:
			next();
			break;
		case 37:
			prev();
			break;
		
	}
	
});

$('#start').live('click', function(){
	change(_pos=0);
	$('#help').remove();
	$('#container').show();
	window.open('controller.html', 'controlbox', "height=300,location=0,menubar=0,scrollbars=0,status=0,toolbar=0,width=800");
});

$(document).ready(function(){
	//change(_pos=0);
});