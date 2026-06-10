$(document).ready(function () {
    ajax_button_click($('#new-button'),'dark',window.location.href,() => {return {type:'new',};},() => location.reload(),norm_wrap);
});