$(document).ready(function(){

    $("#add-item").click(function(){
        $("#add-item-modal").modal("show");
    });



    $("#my-items-col").on("click", ".edit-item", function(){
        $("#edit-item-modal").modal("show")
    });



    $("#confirm-add-item").click(function(){
        url="/catalog/createitem"
        
        console.log("About to send ajax request");

        data = {};
        data.name = "meow this_is_test_name";
        data.category = 5
        data.description = "meow, this is test key data";

        $.ajax({
            contentType: 'application/json',
            dataType: 'json',
            type: 'POST',
            url: url, 
            data: JSON.stringify(data),
            success: function(data){
                console.log("ajax request success")
            },
            error: function(data){
                console.log("ajax request failure")
            },
        });
    });


});