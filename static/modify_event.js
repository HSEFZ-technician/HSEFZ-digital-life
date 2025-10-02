function comb_data(data) {
    res = '';
    let l = data.length;
    for (let i = 0; i < l; i++) {
        res += '<tr><td>' + (i + 1) + '</td><td>' + data[i]['n'] + '</td><td><span>' + data[i]['e'] + '</span></td><td><span>' + data[i]['g'] + '</span></td></tr>';
    }
    return res;
}
function fresh_table(data) {
    $('#table-locked').html(comb_data(data['locked']));
    $('#table-other').html(comb_data(data['other']));
}
$(document).ready(function () {
    ajax_button_click($('#save-button'),'dark',window.location.href,
                      () => {return {type:'save',data:convert_form_data_to_json($('#id-setting_modify_event_form'))};},
                      () => {},
                      norm_wrap);
    ajax_button_click($('#new-button'),'dark',window.location.href,
                      () => {return {type:'new'};},
                      () => {
                        clear_form($('#id-setting_modify_event_form'));
                        $('#table-locked').html('');
                        $('#table-other').html('');
                        $('#optional-content').show();
                        $('#new-button').hide();
                        $('#save-button').show();
                        $('#delete-button').show();
                        for (let i in data['data']) {
                            obj = $('#id_' + i);
                            if (obj.prop('type') == 'checkbox') {
                                obj.prop('checked', data['data'][i]);
                            } else {
                                obj.val(data['data'][i]);
                            }
                        }
                      },
                      norm_wrap);
    ajax_button_click($('#delete-button'),'dark',window.location.href,
                      () => {return {type:'delete'};},
                      () => {
                        clear_form($('#id-setting_modify_event_form'));
                        $('#table-locked').html('');
                        $('#table-other').html('');
                        $('#optional-content').hide();
                        $('#new-button').show();
                        $('#save-button').hide();
                        $('#delete-button').hide();
                      },
                      del_wrap);
    ajax_button_click($('#add-button'),'dark',window.location.href,
                      (result_value) => {return {type:'add','email':result_value};},
                      (data) => {fresh_table(data['data']);},function(data_function,f){input_wrap('完整邮箱地址',data_function,f);});
    ajax_button_click($('#remove-button'),'dark',window.location.href,
                      (result_value) => {return {type:'remove','email':result_value};},
                      (data) => {fresh_table(data['data']);},function(data_function,f){input_wrap('完整邮箱地址',data_function,f);});
    $('#download-button').on('click', function () {
        $('#download-table').table2csv({ filename: 'name_list.csv' });
    });
});
