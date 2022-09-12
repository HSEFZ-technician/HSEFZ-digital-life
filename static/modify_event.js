function confirm_delete(f){
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
          f();
        }
    })
}
function comb_data(data){
    res='';
    let l=data.length;
    for(let i=0;i<l;i++){
        res+='<tr><td>'+(i+1)+'</td><td>'+data[i]['n']+'</td><td><span>'+data[i]['e']+'</span></td><td><span>'+data[i]['g']+'</span></td></tr>';
    }
    return res;
}
function fresh_table(data){
    $('#table-locked').html(comb_data(data['locked']));
    $('#table-other').html(comb_data(data['other']));
}
$(document).ready(function(){
    $('#id-setting_modify_event_form').on('submit',function(e){
        e.preventDefault();
        $('#save-button').html('<div style="display: flex;"><div class="spinner-border text-dark"></div></div>');
        $('#save-button').prop('disabled',true);
        let serialize_data=convert_form_data_to_json($(this));
        $.ajax({
            url: window.location.href,
            method: 'post',
            dataType: 'json',
            contentType: "application/json",
            data:JSON.stringify({
                type:'save',
                data:serialize_data,
            }),
            success: function (data,status) {
                let button = $('#save-button');
                button.prop('disabled', false);
                button.html('保存');
                if(data.code==1){
                    Swal.fire({
                        title: 'Success',
                        text: data['message'],
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
                let button = $('#save-button');
                button.prop('disabled', false);
                button.html('保存');
                Swal.fire({
                    title: 'Failure',
                    text: '请求错误',
                    icon: 'error'
                });
            }
        });
    });
    $('#new-button').on('click',function(e){
        $(this).html('<div style="display: flex;"><div class="spinner-border text-dark"></div></div>');
        $(this).prop('disabled',true);
        $.ajax({
            url: window.location.href,
            method: 'post',
            dataType: 'json',
            contentType: "application/json",
            data:JSON.stringify({
                type:'new',
            }),
            success: function (data,status) {
                let button = $('#new-button');
                button.prop('disabled', false);
                button.html('新建');
                if(data.code==1){
                    Swal.fire({
                        title: 'Success',
                        text: data['message'],
                        icon: 'success',
                    });
                    clear_form($('#id-setting_modify_event_form'));
                    $('#table-locked').html('');
                    $('#table-other').html('');
                    $('#optional-content').show();
                    $('#new-button').hide();
                    $('#save-button').show();
                    $('#delete-button').show();
                    for(let i in data['data']){
                        obj=$('#id_'+i);
                        if(obj.prop('type')=='checkbox'){
                            obj.prop('checked',data['data'][i]);
                        }else{
                            obj.val(data['data'][i]);
                        }
                    }
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
                let button = $('#new-button');
                button.prop('disabled', false);
                button.html('新建');
                Swal.fire({
                    title: 'Failure',
                    text: '请求错误',
                    icon: 'error'
                });
            }
        });
    });
    $('#delete-button').on('click',function(){
        confirm_delete(function(){
            let button=$('#delete-button');
            button.html('<div style="display: flex;"><div class="spinner-border text-dark"></div></div>');
            button.prop('disabled',true);
            $.ajax({
                url: window.location.href,
                method: 'post',
                dataType: 'json',
                contentType: "application/json",
                data:JSON.stringify({
                    type:'delete',
                }),
                success: function (data,status) {
                    let button = $('#delete-button');
                    button.prop('disabled', false);
                    button.html('删除');
                    if(data.code==1){
                        Swal.fire({
                            title: 'Success',
                            text: data['message'],
                            icon: 'success',
                        });
                        clear_form($('#id-setting_modify_event_form'));
                        $('#table-locked').html('');
                        $('#table-other').html('');
                        $('#optional-content').hide();
                        $('#new-button').show();
                        $('#save-button').hide();
                        $('#delete-button').hide();
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
                    let button = $('#delete-button');
                    button.prop('disabled', false);
                    button.html('删除');
                    Swal.fire({
                        title: 'Failure',
                        text: '请求错误',
                        icon: 'error'
                    });
                }
            });
        });
    });
    $('#add-button').on('click',function(){
        Swal.fire({
            title: '完整邮箱地址',
            input: 'text',
            inputAttributes: {
                autocapitalize: 'off'
            },
            showCancelButton: true,
            confirmButtonText: '提交',
        }).then((result) => {
            if (result.isConfirmed) {
                let button=$('#add-button');
                button.html('<div style="display: flex;"><div class="spinner-border text-dark"></div></div>');
                button.prop('disabled',true);
                $.ajax({
                    url: window.location.href,
                    method: 'post',
                    dataType: 'json',
                    contentType: "application/json",
                    data:JSON.stringify({
                        type:'add',
                        email:result.value,
                    }),
                    success: function (data,status) {
                        let button = $('#add-button');
                        button.prop('disabled', false);
                        button.html('添加');
                        if(data.code==1){
                            Swal.fire({
                                title: 'Success',
                                text: data['message'],
                                icon: 'success',
                            });
                            fresh_table(data['data']);
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
                        let button = $('#add-button');
                        button.prop('disabled', false);
                        button.html('添加');
                        Swal.fire({
                            title: 'Failure',
                            text: '请求错误',
                            icon: 'error'
                        });
                    }
                });
            }
        })
    });
    $('#remove-button').on('click',function(){
        Swal.fire({
            title: '完整邮箱地址',
            input: 'text',
            inputAttributes: {
                autocapitalize: 'off'
            },
            showCancelButton: true,
            confirmButtonText: '提交',
        }).then((result) => {
            if (result.isConfirmed) {
                let button=$('#remove-button');
                button.html('<div style="display: flex;"><div class="spinner-border text-dark"></div></div>');
                button.prop('disabled',true);
                $.ajax({
                    url: window.location.href,
                    method: 'post',
                    dataType: 'json',
                    contentType: "application/json",
                    data:JSON.stringify({
                        type:'remove',
                        email:result.value,
                    }),
                    success: function (data,status) {
                        let button = $('#remove-button');
                        button.prop('disabled', false);
                        button.html('删除');
                        if(data.code==1){
                            Swal.fire({
                                title: 'Success',
                                text: data['message'],
                                icon: 'success',
                            });
                            fresh_table(data['data']);
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
                        let button = $('#remove-button');
                        button.prop('disabled', false);
                        button.html('删除');
                        Swal.fire({
                            title: 'Failure',
                            text: '请求错误',
                            icon: 'error'
                        });
                    }
                });
            }
        })
    });
    $('#download-button').on('click',function(){
        $('#download-table').table2csv({filename:'name_list.csv'});
    });
});