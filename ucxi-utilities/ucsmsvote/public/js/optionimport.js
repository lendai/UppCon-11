function getCosplayers() {
    var lax = [
        {
            "index": 1,
            "id": 4,
            "name": "Talim",
            "source": "Soul calibur lll",
            "user": {
                "uuid": "799ef39c-e752-4fdf-93be-717f2b0aaecb",
                "firstname": "Hanna",
                "lastname": "Andersson",
                "city": "Uppsala",
                "country": "Sverige"
            }
        },
        {
            "index": 2,
            "id": 10,
            "name": "Rayman",
            "source": "Rayman 3: Hoodlum Havoc",
            "user": {
                "uuid": "d246438d-f3a1-4add-b6e4-9529d520adf7",
                "firstname": "Sabina",
                "lastname": "Mangal",
                "city": "Lund",
                "country": "Sverige"
            }
        },
    ];

    return lax;
};


function importCosplayers() {
    var brax = getCosplayers();
    $.each(brax, function(i,n) {
        var name_string = n.user.firstname + " " + n.user.lastname.substr(0,1) + ' som ' + n['name'];
        var params = {
            shortname: 'cosplay',
            id: n['index'],
            external_id: n['id'],
            name: name_string,
        };
        $.post('/option', params, ajaxResponse, 'json');
    });
}

