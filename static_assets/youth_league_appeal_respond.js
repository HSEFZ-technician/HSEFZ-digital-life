$(document).ready(function(){
    $(".appeal-respond-submit").click(function(){
      $.post("#",
      {
        appeal_id: this.getAttribute("appeal_id"),
        appeal_respond_content: $("#appeal-respond-input-" + this.getAttribute("appeal_id"))[0].value
      },
      function(data,status){
        location.reload();
      });
    });
  });

function setAppealId(appeal_id) {
    $('#appeal-respond-id')[0].setAttribute('value', appeal_id);
}