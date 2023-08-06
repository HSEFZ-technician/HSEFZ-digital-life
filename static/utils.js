function clear_form(f) {
    f.find('input')
    .not(':button, :submit, :reset, :hidden')
    .val('')
    .prop('checked', false)
    .prop('selected', false);
}
function convert_form_data_to_json(f) {
    return f.serializeArray().reduce(function(obj, item) {
        obj[item.name] = item.value;
        return obj;
    }, {});
}
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
String.prototype.format = function(args) {
    if (arguments.length > 0) {
        var result = this;
        if (arguments.length == 1 && typeof(args) == "object") {
            for (var key in args) {
                var reg = new RegExp("({" + key + "})", "g");
                result = result.replace(reg, args[key]);
            }
        } else {
            for (var i = 0; i < arguments.length; i++) {
                if (arguments[i] == undefined) {
                    return "";
                } else {
                    var reg = new RegExp("({[" + i + "]})", "g");
                    result = result.replace(reg, arguments[i]);
                }
            }
        }
        return result;
    } else {
        return this;
    }
}
function csrfSafeMethod(method) {
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}
$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
        }
    }
});
function del_wrap(data_function,f){
    Swal.fire({
        title: '请确认',
        text: "删除操作不可逆!",
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#3085d6',
        cancelButtonColor: '#d33',
        confirmButtonText: '确认删除',
        cancelButtonText: '取消',
    }).then((result)=>{
        if (result.isConfirmed) {
            f(data_function());
        }
    })
}
function norm_wrap(data_function,f){
    f(data_function());
}
function input_wrap(title,data_function,f){
    Swal.fire({
        title: title,
        input: 'text',
        inputAttributes: {
            autocapitalize: 'off'
        },
        showCancelButton: true,
        confirmButtonText: '提交',
    }).then((result)=>{
        if (result.isConfirmed) {
            f(data_function(result.value));
        }
    })
}
function ajax_button_click(button,spinner_style,url,data_function,success_function,wrap_func){
    let original_content = button.html();
    function recover(){
        button.html(original_content);
        button.prop('disabled', false);
    }
    button.on('click',function(){
        wrap_func(data_function,function(processed_data){
            button.html('<div style="display: flex;"><div class="spinner-border text-'+spinner_style+'"></div></div>');
            button.prop('disabled',true);
            $.ajax({
                url: url,
                method: 'post',
                dataType: 'json',
                contentType: "application/json",
                data:JSON.stringify(processed_data),
                success: function (data,status) {
                    recover();
                    if(data.code==1){
                        Swal.fire({
                            title: 'Success',
                            text: data['message'],
                            icon: 'success',
                        });
                        success_function(data);
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
                    recover();
                    Swal.fire({
                        title: 'Failure',
                        text: '请求错误',
                        icon: 'error'
                    });
                }
            });
        });
    });
}