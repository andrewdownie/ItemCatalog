/////
/////                   Events
/////
$(document).ready(function(){


    $("#add-item").click(function(){
        $("#add-item-modal").modal("show");
        ValidateItemName("#add-item-name", "#add-error-message");
    });


    $("#my-items-col").on("click", ".edit-item", function(){
        $("#edit-item-modal").modal("show")
        LoadItemValuesIntoEditModal($(this).parent());
        ValidateItemName("#edit-item-name", "#edit-error-message");
    });


    $("#confirm-add-item").click(function(){
        AddItem();
    });


    $("#confirm-edit-item").click(function(){
        EditItem();
    });


    $("#edit-item-name").on('keyup', function(event){
        ValidateItemName("#edit-item-name", "#edit-error-message")
    });


    $("#add-item-name").on('keyup', function(event){
        ValidateItemName("#add-item-name", "#add-error-message")
    });


});


/////
/////                   Manage
/////
function IsValidItemName(item_name){
    var validCharactersOnly = new RegExp('^([a-zA-Z0-9_-]*)$')

    if(item_name.length === 0){
        return "Item name cannot be empty.";
    }

    if(validCharactersOnly.test(item_name) === false){
        return "Item names can only contain alphanumeric characters, dashes and underscores.";
    }

    return true;
}


function ValidateItemName(inputBoxSelector, errorMessageSelector){
    current_item_name = $(inputBoxSelector).val()

    valid_item_name = IsValidItemName(current_item_name)

    if(valid_item_name != true){
        $(errorMessageSelector).text(valid_item_name); 
    }
    else{
        $(errorMessageSelector).text("")
    }
}


function LoadItemValuesIntoEditModal(item_card){
    var item_id = item_card.attr("itemid");
    var item_name = item_card.find(".item-name").text()
    var item_category_id = item_card.find(".item-cat").attr("categoryid")
    var item_desc = item_card.find(".item-desc").text()

    $("#edit-item-name").val(item_name)
    $("#edit-item-name").attr("itemid", item_id)
    $("#edit-item-category").val(item_category_id).change();
    $("#edit-item-description").text(item_desc);
}


/////
/////                   Ajax Calls
/////
function AddItem(){
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
}


function EditItem(){
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
}

