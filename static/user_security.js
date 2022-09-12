$(document).ready(function(){
    $('#id-setting_modify_password_form').on('submit',
        function(e) {
            e.preventDefault();
            let data = convert_form_data_to_json($(this));
            clear_form($(this));
            let url = $(this).attr('action');
            let button = $(this).find('#submit-id-submit')
            button.prop('disabled', true);
            button.html('<div class="spinner-border text-info"></div>')
            $.ajax({
                url: url,
                data: JSON.stringify(data),
                method: "post",
                dataType: "json",
                contentType: 'application/json',
                success: function (data,status) {
                    let button = $('#id-setting_modify_password_form #submit-id-submit');
                    button.prop('disabled', false);
                    button.html('提交');
                    if(data.code==1){
                        Swal.fire({
                            title: 'Success',
                            text: data.message,
                            icon: 'success',
                        });
                    }else{
                        if(data.message){
                            Swal.fire({
                                title: 'Failure',
                                text: data.message,
                                icon: 'error'
                            });
                        }else{
                            Swal.fire({
                                title: 'Failure',
                                text: '请求错误',
                                icon: 'error'
                            });
                        }
                    }
                },
                error: function(XMLHttpRequest, textStatus, errorThrown) {
                    var button = $('#id-setting_modify_password_form #submit-id-submit');
                    button.prop('disabled', false);
                    button.html('提交');
                    Swal.fire({
                        title: 'Failure',
                        text: '请求错误',
                        icon: 'error'
                    });
                }
            });
        }
    );
});