$(document).ready(function(){


    $("#all-categories-col").on("click", ".category-link", function(){
        var cat_id = this.id;
        var cat_name = $(this).text().trim()
        alert(cat_name)


        rest_url = "/catalog/" + cat_name + "/items"


        //dis wur wii select all the items we need to select items of category id
        //so we ajax to the back end, so it can make a sql request
        $.ajax({
            contentType: 'application/json',
            dataType: 'json',
            type: 'GET',
            url: rest_url, 
            success: function(data){
                console.log("Request items of category: success")
                console.log(data)
            },
            error: function(data){
                console.log("Request items of category: failure");
                console.log(data);
            },
        });


    });


});