var appeal_links;
var appeal_window_label;

$(document).ready(function () {
    appeal_links = $('.appeal-link');
    appeal_window_label = $('#appeal-window-label');
});

function showAppealWindow(appeal_current_num) {
    var appeal_current_test_title = $('#test-title-'+appeal_current_num).html();
    appeal_window_label[0].innerHTML = '申诉（考试名称：' + appeal_current_test_title + '）';
    $('#appeal-window-test-id')[0].setAttribute('value', appeal_current_num);
    console.log(appeal_current_num);
}

