$(document).ready(function(){


    $("#all-categories-col").on("click", ".category-link", function(){
        var cat_id = this.id;
        alert(cat_id)


        //dis wur wii select all the items we need to select items of category id
        //so we ajax to the back end, so it can make a sql request



    });


});