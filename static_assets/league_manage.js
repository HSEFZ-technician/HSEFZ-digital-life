$(document).ready(function () {
    ajax_button_click($('#new-button'),'dark','/league/create_league',() => {return {type:'new',};},() => location.reload(),norm_wrap);
});