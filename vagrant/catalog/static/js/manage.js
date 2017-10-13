$(document).ready(function(){

    $("#add-item").click(function(){
        $("#add-item-modal").modal("show");
    });

    $("#edit-item-name").change(function(){
        //alert("meow")
    });


    $("#edit-item-name").keypress(function(event){
        var keycode = (event.keyCode ? event.keyCode : event.which);
        valid_item_name = ValidItemName( $("#edit-item-name").val() )
        alert(valid_item_name)
        if(valid_item_name != true){
            $("#edit-error-message").text(valid_item_name);
        }

    });


    $("#my-items-col").on("click", ".edit-item", function(){
        $("#edit-item-modal").modal("show")
    });



    $("#my-items-col").on("click", ".edit-item", function(){
        var item_card = $(this).parent();

        var item_id = item_card.attr("itemid");
        var item_name = item_card.find(".item-name").text()
        var item_category_id = item_card.find(".item-cat").attr("categoryid")
        var item_desc = item_card.find(".item-desc").text()
        //var item_category_name = item_card.find(".item-cat").text()


        $("#edit-item-name").val(item_name)
        $("#edit-item-name").attr("itemid", item_id)
        $("#edit-item-category").val(item_category_id).change();
        $("#edit-item-description").text(item_desc);

    });


    $("#confirm-add-item").click(function(){
        url="/catalog/createitem"
        
        console.log("About to send ajax request");

        data = {};
        data.name = $("#add-item-name").val()
        data.category = Number($("#add-item-category").val())
        data.description = $("#add-item-description").val()
        alert(data.category)

        $.ajax({
            contentType: 'application/json',
            dataType: 'json',
            type: 'POST',
            url: url, 
            data: JSON.stringify(data),
            success: function(data){
                console.log("ajax request success :: add item")
            },
            error: function(data){
                console.log("ajax request failure :: add item")
            },
        });
    });


    $("#confirm-edit-item").click(function(){
        url="/catalog/edititem"
        
        console.log("About to send ajax request to edit item");

        data = {};
        data.item_id = Number($("#edit-item-name").attr("itemid"))
        data.name = $("#edit-item-name").val();
        data.category = Number($("#edit-item-category").val());
        data.description = $("#edit-item-description").val();

        $.ajax({
            contentType: 'application/json',
            dataType: 'json',
            type: 'POST',
            url: url, 
            data: JSON.stringify(data),
            success: function(data){
                console.log("ajax request success :: edit item")
            },
            error: function(data){
                console.log("ajax request failure :: edit item")
            },
        });
    });


});


function ValidItemName(item_name){
    var validCharactersOnly = new RegExp('^([a-z0-9_-]+)$')
    alert(item_name)


    if(validCharactersOnly.test(item_name) === false){
        return "Item names can only contain alphanumeric, dashes and underscores.";
    }


    return true;
}