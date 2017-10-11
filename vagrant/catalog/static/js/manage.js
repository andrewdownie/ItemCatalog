$(document).ready(function(){
    $("#add-item").click(function(){
        $("#add-item-modal").modal("show");
    });



    $("#my-items-col").on("click", ".edit-item", function(){
        $("#edit-item-modal").modal("show")
    });

    $("#confirm-add-item").click(function(){
        url="/catalog/createitem"

        $.ajax({
            contentType: 'application/json',
            dataType: 'json',
            type: 'POST',
            url: url, 
            success: function(data){

            },
            error: function(data){

            },
        });
    });
});