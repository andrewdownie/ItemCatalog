card_count = 0
/////
/////                   Events
/////
$(document).ready(function(){

    card_count = $("#item-card-row").children().length

    if(card_count === 0){
        $("#item-card-row").prepend("<p>You don't have any items, maybe you should add some?</p>")
    }


    $("#add-item").click(function(){
        $("#add-item-modal").modal("show");
        ValidateItemName("#add-item-name", "#confirm-add-item", "#add-error-message");
    });


    $("#my-items-col").on("click", ".edit-item", function(){
        $("#edit-item-modal").modal("show")
        LoadItemValuesIntoEditModal($(this).parent());
        ValidateItemName("#edit-item-name", "#confirm-edit-item", "#edit-error-message");
    });


    $("#confirm-add-item").click(function(){
        HideAlerts();
        AddItem();
    });


    $("#confirm-edit-item").click(function(){
        HideAlerts();
        EditItem();
    });


    $("#confirm-delete-item").click(function(){
        DeleteItem();
    });


    $("#edit-item-name").on('keyup', function(event){
        ValidateItemName("#edit-item-name", "#confirm-edit-item", "#edit-error-message")
    });


    $("#add-item-name").on('keyup', function(event){
        ValidateItemName("#add-item-name", "#confirm-add-item", "#add-error-message")
    });


});


/////
/////                   Validate Item Name
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


function ValidateItemName(inputBoxSelector, buttonSelector, errorMessageSelector){
    current_item_name = $(inputBoxSelector).val()

    valid_item_name = IsValidItemName(current_item_name)

    if(valid_item_name != true){
        $(errorMessageSelector).text(valid_item_name); 
        $(buttonSelector).prop("disabled", true)
    }
    else{
        $(errorMessageSelector).text("")
        $(buttonSelector).prop("disabled", false)
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

    item_data = {};
    item_data.name = $("#add-item-name").val()
    item_data.category = Number($("#add-item-category").val())
    item_data.description = $("#add-item-description").val()
    item_data.category_name = $("#add-item-category option:selected").text()

    $.ajax({
        contentType: 'application/json',
        dataType: 'json',
        type: 'POST',
        url: url, 
        data: JSON.stringify(item_data),
        success: function(data){
            console.log("ajax request success :: add item")
            console.log(data)

            ShowAlert(data);

            if(card_count === 0){
                $("#item-card-row").empty()
            }
            if(data.status == "success"){
                $("#item-card-row").prepend(BuildItemCard(data['item_id'], item_data.name, item_data.category, item_data.category_name, item_data.description))
            }
        },
        error: function(data){
            console.log("ajax request failure :: add item")
            console.log(data)
        },
    });
}


function EditItem(){
    url="/catalog/edititem"
    
    console.log("About to send ajax request to edit item");

    item_data = {};
    item_data.item_id = Number($("#edit-item-name").attr("itemid"))
    item_data.name = $("#edit-item-name").val();
    item_data.description = $("#edit-item-description").val();

    item_data.category = Number($("#edit-item-category").val());
    item_data.category_name = $("#edit-item-category option:selected").text()

    $.ajax({
        contentType: 'application/json',
        dataType: 'json',
        type: 'POST',
        url: url, 
        data: JSON.stringify(item_data),
        success: function(data){
            console.log("ajax request success :: edit item")
            console.log(data)
            ShowAlert(data);

            var item_card = $("#item-" + item_data.item_id)
            item_card.find(".item-name").text(item_data.name)
            item_card.find(".item-desc").text(item_data.description)

            item_card.find(".item-cat").text(item_data.category_name)
            item_card.find(".item-cat").attr("categoryid", item_data.category)
        },
        error: function(data){
            console.log("ajax request failure :: edit item")
            console.log(data)
        },
    });
}

function DeleteItem(){
    url="/catalog/deleteitem"
    
    console.log("About to send ajax request to delete item");

    item_data = {};
    item_data.item_id = Number($("#edit-item-name").attr("itemid"))

    $.ajax({
        contentType: 'application/json',
        dataType: 'json',
        type: 'POST',
        url: url, 
        data: JSON.stringify(item_data),
        success: function(data){
            console.log("ajax request success :: delete item")
            console.log(data)

            $("#item-" + item_data.item_id).remove()

        },
        error: function(data){
            console.log("ajax request failure :: delete item")
            console.log(data)
        },
    });
}


/////
/////                   Alerts
/////
function HideAlerts(){
    $("#success-alert").hide();
    $("#failure-alert").hide();
}

function ShowAlert(ajaxData){

    var messages = "<ul>";
    for(var i = 0; i < ajaxData.messages.length; i++){
        messages += "<li>" 
        messages += ajaxData.messages[i]
        messages += "</li>" 
    }
    messages += "</ul>";

    if(ajaxData.status == "success"){
        $("#success-alert").show();
        $("#success-alert-message").html(messages)
    }
    else{
        $("#failure-alert").show();
        $("#failure-alert-message").html(messages);
    }
}

function BuildItemCard(item_id, item_name, category_id, category_name, item_desc){
    var item_card = `
    <div class="item-card-container col-md-4">
        <div itemid="` + item_id + `" id="item-` + item_id + `" class="item-card col-xs-12">
            <h3 class="page-header item-name">` + item_name + `</h3>
            <h4>Category: <span categoryid="` + category_id + `" class="item-cat">` + category_name + `</span> </h4>
            <p class="item-desc">` + item_desc + `</p>
            <button class="btn btn-primary edit-item">Edit</button>
        </div>
    </div>
    `

    return item_card
}