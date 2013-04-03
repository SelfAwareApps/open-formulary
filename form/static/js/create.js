$(document).ready( function(){
    $('h3.drugsect').click( function(e){
        console.log(this);
        $h3 = $(this);
        $h3.children('i').toggleClass('icon-chevron-right').toggleClass('icon-chevron-down');
        window.h3 = $h3;
        $druglist = $h3.siblings('div');
        if($druglist.is(':visible')){
            $druglist.slideUp();
        }else{
            $druglist.slideDown();
        }
        $h3.next('div')
    });
});
