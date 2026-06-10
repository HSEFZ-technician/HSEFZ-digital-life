$(document).ready(function () {
    ajax_button_click($('#new-button'),'dark','/league/class_team_manage',() => {return {type:'new',};},() => location.reload(),norm_wrap);
});