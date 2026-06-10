$(document).ready(function(){
    ajax_button_click($('#submit-id-submit'),'info',$('#id-setting_modify_password_form').attr('action'),
                      () => {return convert_form_data_to_json($('#id-setting_modify_password_form'));},
                      () => {},(data_function,f) => {data = data_function();clear_form($('#id-setting_modify_password_form'));f(data);});
});