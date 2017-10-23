$(document).ready(function(){

    //Count how many items there are, and if there are zero, display a message
    item_count = $("#items-container").children().length
    if(item_count === 0){
        $("#items-container").prepend("<p>There are no items :(</p><br><br>")
    }


    //Click to view a specific category
    $("#all-categories-col").on("click", ".category-link", function(){
        var cat_id = this.id;
        var cat_name = $(this).text().trim();

        rest_url = "/catalog/" + cat_name + "/items";

        window.location = location.origin + rest_url;

    });


    //Click to view a specific item
    $("#items-col").on("click", ".item-link", function(){
        var item_name = $(this).text().trim();
        var item_id = this.id;

        var cat_name = $(this).parent().children('.item-category').text()
        
        rest_url = "/catalog/" + cat_name + "/" + item_name;
        window.location = location.origin + rest_url;
    });

});