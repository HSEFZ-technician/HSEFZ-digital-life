$(document).ready(function(){
    ajax_button_click($('#save-button'),'dark',window.location.href,
                      () => {return {type:'save',data:convert_form_data_to_json($('#id-setting_modify_class_team_form'))};},
                      () => {},norm_wrap);
    ajax_button_click($('#delete-button'),'dark',window.location.href,() => {return {type:'delete',};},() => location.assign(manage_url),del_wrap);
});
$.ajaxSetup({
    data:{csrfmiddlewaretoken:'{{ csrf_token }}'}
});