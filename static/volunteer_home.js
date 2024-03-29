$(document).ready(function () {
    ajax_button_click($('#check-button'), 'dark', window.location.href,
        () => { return { type: 'check' }; },
        () => { location.reload() }, check_wrap);
});