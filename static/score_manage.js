$(document).ready(function () {
    ajax_button_click($('#new-button'),'dark',window.location.href,() => {return {type:'new',};},() => location.reload(),norm_wrap);
});
$(document).ready(function () {
    ajax_button_click($('#import-button'),'dark',window.location.href,() => {return {type:'import',};},() => location.reload(),norm_wrap);
});
$(document).ready(function () {
    ajax_button_click($('#export-button'),'dark',window.location.href,() => {return {type:'export',};},() => location.reload(),norm_wrap);
});
