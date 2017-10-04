$(document).ready(function(){


    $("#all-categories-col").on("click", ".category-link", function(){
        var cat_id = this.id;
        var cat_name = $(this).text().trim();

        rest_url = "/catalog/" + cat_name + "/items";

        window.location = location.origin + rest_url;

    });



    $("#items-col").on("click", ".item-link", function(){
        var item_name = $(this).text().trim();
        var item_id = this.id;

        //TODO: currently not properly getting the name of the items category
        var cat_name = $(this).parent().children('.item-category').text() //TODO: get name of category that is stored below
        alert(cat_name)
        
        rest_url = "/catalog/" + cat_name + "/" + item_name;
        window.location = location.origin + rest_url;
    });

});