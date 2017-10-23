card_count = 0
/////
/////                   Events
/////
$(document).ready(function(){

    //Count how many items the user has, and if they have zero, display a message
    card_count = $("#item-card-row").children().length
    if(card_count === 0){
        $("#item-card-row").prepend("<p>You don't have any items, maybe you should add some?</p>")
    }


    //Click to show add item modal
    $("#add-item").click(function(){
        $("#add-item-modal").modal("show");
        ValidateItemName("#add-item-name", "#confirm-add-item", "#add-error-message");
    });


    //Click to show edit item modal
    $("#my-items-col").on("click", ".edit-item", function(){
        $("#edit-item-modal").modal("show")
        LoadItemValuesIntoEditModal($(this).parent());
        ValidateItemName("#edit-item-name", "#confirm-edit-item", "#edit-error-message");
    });


    //Click to confirm adding an item, and save it to the database through an ajax call
    $("#confirm-add-item").click(function(){
        HideAlerts();
        ajax_AddItem();
    });


    //Click to confirm editing an item, and save it to the database through an ajax call
    $("#confirm-edit-item").click(function(){
        HideAlerts();
        ajax_EditItem();
    });


    //Click to delete an item
    $("#confirm-delete-item").click(function(){
        ajax_DeleteItem();
    });

    //Keyup to validate item name in real time while adding an item
    $("#edit-item-name").on('keyup', function(event){
        ValidateItemName("#edit-item-name", "#confirm-edit-item", "#edit-error-message")
    });


    //Keyup to validate an item name in real time while editing an item
    $("#add-item-name").on('keyup', function(event){
        ValidateItemName("#add-item-name", "#confirm-add-item", "#add-error-message")
    });


});


/////
/////                   Validate Item Name
/////
function IsValidItemName(item_name){
    //Test that the given item name only contains: alphanumeric, underscores and dashes,
    //  return true if the item name confirms to this regex, return an error message
    //  expaining what's wrong with the name otherwise.
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
    //Figure out what item a user pressed the edit button on,
    //  and then grab its info, and copy it to the edit item modal
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
function ajax_AddItem(){
    url="/catalog/createitem"
    
    console.log("About to send ajax request");

    //Gather the info we are going to add to the database
    item_data = {};
    item_data.name = $("#add-item-name").val()
    item_data.category = Number($("#add-item-category").val())
    item_data.description = $("#add-item-description").val()
    item_data.category_name = $("#add-item-category option:selected").text()

    //Make the ajax call to add the item to the database
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


            
            if(data.status == "success"){
                //If the user previously had zero cards, and we add a new card, delete the "no cards"
                //  that would be currently present
                if(card_count === 0){
                    $("#item-card-row").empty()
                }
                //Add a card for the newly created item
                $("#item-card-row").prepend(BuildItemCard(data['item_id'], item_data.name, item_data.category, item_data.category_name, item_data.description))
            }
        },
        error: function(data){
            console.log("ajax request failure :: add item")
            console.log(data)
        },
    });
}


function ajax_EditItem(){
    url="/catalog/edititem"
    
    console.log("About to send ajax request to edit item");

    //Gather the info about the item we are going to edit in the database
    item_data = {};
    item_data.item_id = Number($("#edit-item-name").attr("itemid"))
    item_data.name = $("#edit-item-name").val();
    item_data.description = $("#edit-item-description").val();

    item_data.category = Number($("#edit-item-category").val());
    item_data.category_name = $("#edit-item-category option:selected").text()

    //Make the ajax call to edit the item
    $.ajax({
        contentType: 'application/json',
        dataType: 'json',
        type: 'POST',
        url: url, 
        data: JSON.stringify(item_data),
        success: function(data){

            //If the edit item ajax call was successful, show the user an alert,
            //  and update that items card
            console.log("ajax request success :: edit item")
            console.log(data)
            ShowAlert(data);

            if(data.status == "success"){
                var item_card = $("#item-" + item_data.item_id)
                item_card.find(".item-name").text(item_data.name)
                item_card.find(".item-desc").text(item_data.description)

                item_card.find(".item-cat").text(item_data.category_name)
                item_card.find(".item-cat").attr("categoryid", item_data.category)
            }
        },
        error: function(data){
            console.log("ajax request failure :: edit item")
            console.log(data)
        },
    });
}

function ajax_DeleteItem(){
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

            $("#item-" + item_data.item_id).parent().remove()

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
    //Shows the resulting message from the create/edit/delete ajax call
    //  in an on page, bootstrap alert for the user to see

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
    //Builds the html to display a users item. 
    //Used when a user creates an item so the whole page doesn't need to reload.
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