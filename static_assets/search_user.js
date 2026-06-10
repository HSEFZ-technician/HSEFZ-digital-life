$(document).ready(function () {
    ajax_button_click($('#push-button'),'dark',window.location.href,
                      () => {return {type:'push',data:convert_form_data_to_json($('#id-setting_search_user_form'))};},
                      (data) => {if(data.code==1) window.location.href='/volunteer/score_input?id='+data.id;},norm_wrap);
});
