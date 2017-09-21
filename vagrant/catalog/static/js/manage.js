$(document).ready(function(){
    $("#add-item").click(function(){
        $("#add-item-modal").modal("show");
    });



    $("#my-items-col").on("click", ".edit-item", function(){
        $("#edit-item-modal").modal("show")
    });

});