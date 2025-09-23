// const row_content = "<tr><td class='status-content'>{0}</td><td class='name-content'>{1}</td><td><div class='desc-full'><div class='col'>{2}</div>{3}</div></td>{4}<td class='cnum-content'>{5}</td><td class='rnum-content'>{6}</td><td class='op-content'>{7}</td></tr>";

const row_content = "<tr>" +
    "<td class='op-content'>{0}</td>" +      // ← 收藏按钮列
    "<td class='status-content'>{1}</td>" +
    "<td class='name-content'>{2}</td>" +
    "<td><div class='desc-full'><div class='col'>{3}</div>{4}</div></td>" +
    "{5}" +                                       // 类型列
    "<td class='cnum-content'>{6}</td>" +
    "<td class='rnum-content'>{7}</td>" +
    "<td class='op-content'>{8}</td>" +
"</tr>";


function convert_form_data_to_json(data) {
    // console.log("data:", data);
    // console.log("data['data']:", data['data']);

    let result = '';
    let dtype = data['display_type'];
    // var disa = false;
    // for (c of data['data']) {
    //     if (c['status'] == 4 || c['status'] == 5) {
    //         disa = true;
    //         break;
    //     }
    // }
    for (c of data['data']) {
        let name = c['name'], logo = '', desc = c['desc'], type_div = '', cnum = c['cnum'], rnum = c['rnum'], class_id = c['id'], op_content = '', full_desc_button = '';
        if (c['status'] == 4 || c['status'] == 5 || c['status'] == 7) {
            logo = "<span><i class='fa-solid fa-check fa-lg'></i></span>";
        } else if (c['status'] == 2) {
            logo = "<span><i class='fa-solid fa-ban fa-lg'></i></span>";
        } else if (c['status'] == 3) {
            logo = "<span style='margin-left:0.15rem;'><i class='fa-solid fa-xmark fa-xl'></i></span>";
        }
        if (dtype) {
            type_div = "<td class='type-content'>{0}</td>".format(data['types'][c['type']]);
        } else {
            type_div = "<td class='type-content'></td>";  // 保证占位
        }

        if (c['status'] == 0) {
            op_content = "<button class='btn btn-primary sign-up' id='{0}'>报名</button>".format(class_id);
        }
        else if (c['status'] == 1) {
            op_content = "<button class='btn btn-primary' id='{0}' disabled>不可报名</button>".format(class_id);
        }
        else if (c['status'] == 2) {
            op_content = "<button class='btn btn-danger' id='{0}' disabled>不可报名</button>".format(class_id);
        }
        else if (c['status'] == 3) {
            op_content = "<button class='btn btn-primary' id='{0}' disabled>已满</button>".format(class_id);
        }
        else if (c['status'] == 4) {
            op_content = "<button class='btn btn-danger cancel-sign-up' id='{0}'>取消报名</button>".format(class_id);
        }
        else if (c['status'] == 5) {
            op_content = "<button class='btn btn-danger' id='{0}' disabled>不可取消</button>".format(class_id);
        }
        else if (c['status'] == 6) {
            op_content = "<button class='btn btn-primary id='{0}' disabled>未开始</button>".format(class_id);
        }
        else {
            op_content = "<button class='btn btn-danger id='{0}' disabled>未开始</button>".format(class_id);
        }
        if (c['full_desc']) {
            full_desc_button = "<a href='{0}'>详情</a>".format(c['link']);
        }

        if (c['is_favorite'] == 1) {
            favorite_content = "<button class='btn btn-primary cancel-favorite' id='{0}'>取消收藏</button>".format(class_id);
        }

        else {
            favorite_content = "<button class='btn btn-primary add-favorite' id='{0}'>收藏</button>".format(class_id);
        }

        // result += row_content.format(favorite_content, logo, name, desc, full_desc_button, type_div, cnum, rnum, op_content);
        result += `
        <tr>
            <td class="op-content">${favorite_content}</td>
            <td class="status-content">${logo}</td>
            <td class="name-content">${name}</td>
            <td><div class="desc-full"><div class="col">${desc}</div>${full_desc_button}</div></td>
            ${type_div}
            <td class="cnum-content">${cnum}</td>
            <td class="rnum-content">${rnum}</td>
            <td class="op-content">${op_content}</td>
        </tr>
        `;
        // console.log(c['id'], c['is_favorite'], favorite_content);

    }
    // console.log(c['id'], c['is_favorite'], favorite_content);
    return result;
}


function refresh(data) {
    $('#sign-up-table-tbody').html(convert_form_data_to_json(data));
    $('.add-favorite').on('click', add_favorite);
    $('.cancel-favorite').on('click', remove_favorite);
    $('.sign-up').on('click', register);
    $('.cancel-sign-up').on('click', cancel_register);
    $('.btn-full-desc').on('click', jump_desc);
}

// function refresh(data) {
//     $('#sign-up-table-tbody').html(convert_form_data_to_json(data));
//     $('.sign-up').on('click', register);
//     $('.cancel-sign-up').on('click', cancel_register);
//     $('.btn-full-desc').on('click', jump_desc);
// }

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}


function manual_refresh_succ_h(t) {
    // console.log("refresh data:", res);
    return function (res) {
        t.html('刷新');
        t.prop('disabled', false);
        refresh(res);
        Swal.fire({ title: 'Success', text: '刷新成功', icon: 'success' });
    };
}
function manual_refresh_fail_h(t) {
    return function (res) {
        t.html('刷新');
        t.prop('disabled', false);
        Swal.fire({ title: 'Failure', text: '刷新失败', icon: 'error' });
    };
}
function manual_refresh() {
    console.log("manual_refresh clicked");
    $(this).html('<div style="display: flex;"><div class="spinner-border text-primary"></div></div>');
    $.ajax({
        url: query_url,
        dataType: 'json',
        success: manual_refresh_succ_h($(this)),
        error: manual_refresh_fail_h($(this))
    });
}
function get_result_and_refresh(data) {
    $.ajax({
        url: submit_url,
        data: JSON.stringify(data),
        dataType: 'json',
        method: 'post',
        contentType: 'application/json',
        success: function (data, status) {
            if (data['code'] == 1) {
                refresh(data['data']);
                Swal.fire({
                    title: 'Success',
                    text: data['message'],
                    icon: 'success'
                });
            } else {
                refresh(data['data']);
                Swal.fire({
                    title: 'Failure',
                    text: data['message'],
                    icon: 'error'
                });
            }
        },
        error: function (XMLHttpRequest, textStatus, errorThrown) {
            Swal.fire({
                title: 'Failure',
                text: '请求错误',
                icon: 'error'
            });
        }
    })
}
function cancel_register() {
    $(this).html('<div style="display: flex;"><div class="spinner-border text-info"></div></div>');
    $(this).prop('disabled', true);
    get_result_and_refresh({ class_id: parseInt($(this).attr('id')), type: 'cancel_register' });
}
function register() {
    $(this).html('<div style="display: flex;"><div class="spinner-border text-dark"></div></div>');
    $(this).prop('disabled', true);
    get_result_and_refresh({ class_id: parseInt($(this).attr('id')), type: 'register' });
}
function jump_desc() {
    window.open((desc_url + '?id={0}').format($(this).attr('id')), '_blank');
}

// 收藏函数
function add_favorite() {
    const btn = $(this);
    btn.html('<div style="display: flex;"><div class="spinner-border text-warning"></div></div>');
    btn.prop('disabled', true);

    get_result_and_refresh({
        class_id: parseInt(btn.attr('id')), // 用 id 属性
        type: 'add_favorite'
    });
}

// 取消收藏函数
function remove_favorite() {
    const btn = $(this);
    btn.html('<div style="display: flex;"><div class="spinner-border text-warning"></div></div>');
    btn.prop('disabled', true);

    get_result_and_refresh({
        class_id: parseInt(btn.attr('id')),
        type: 'remove_favorite'
    });
}


$(document).ready(function () {
    $('.sign-up').on('click', register);
    $('.cancel-sign-up').on('click', cancel_register);
    $('.btn-full-desc').on('click', jump_desc);
    $('.refresh-button').on('click', manual_refresh);
    $('.add-favorite').on('click', add_favorite);
    $('.cancel-favorite').on('click', remove_favorite);
});