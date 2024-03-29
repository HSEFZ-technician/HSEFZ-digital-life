$(document).ready(function () {
    ajax_button_click($('#check-button'), 'dark', window.location.href,
        () => { return { type: 'check' }; },
        () => { }, check_wrap);
});