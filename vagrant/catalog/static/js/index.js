$(document).ready(function(){


    $("#all-categories-col").on("click", ".category-link", function(){
        var cat_id = this.id;
        var cat_name = $(this).text().trim()

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
                $("#items-header").text(cat_name)

                $("#items-container").empty()
                for(i = 0; i < data.length; i++){
                    item = ItemTemplate(data[i]);
                    $("#items-container").append(item)
                }

            },
            error: function(data){
                console.log("Request items of category: failure");
                console.log(data);
            },
        });


    });


});


function ItemTemplate(itemRow){
    var item = `
    <h4><a href="#">{item_name}</a></h4>
    Category: {category_name} 
    <br/>
    <br/>
    `;

    item = item.replace("{item_name}", itemRow['item_name']);
    item = item.replace("{category_name}", itemRow['category_name']);

    return item;
}