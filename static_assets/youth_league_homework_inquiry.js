var appeal_links;
var appeal_window_label;

$(document).ready(function () {
    appeal_links = $('.appeal-link');
    appeal_window_label = $('#appeal-window-label');
});

function showAppealWindow(appeal_current_num) {
    var appeal_current_course_title = $('#course-title-'+appeal_current_num).html();
    appeal_window_label[0].innerHTML = '申诉（课程名称：' + appeal_current_course_title + '）';
    $('#appeal-window-course-id')[0].setAttribute('value', appeal_current_num);
}

// $(document).ready(function () {
//     var appeal_links = $('.appeal-link');
//     var appeal_window_label = $('#appeal-window-label');
//     var appeal_current_num;
//     for (i = 0; i < appeal_links.length; i++) {
//         appeal_current_num = appeal_links[i].getAttribute('course_id');
//         appeal_links[i].onclick = function() {
//             console.log(appeal_current_num);
//             var appeal_current_course_title = $('#course-title-'+appeal_current_num).html();
//             appeal_window_label[0].innerHTML = appeal_current_course_title;
//         };
//     }
// });

