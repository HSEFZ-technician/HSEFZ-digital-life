let group1 = document.getElementById("group-1");
let group2 = document.getElementById("group-2");
let group3 = document.getElementById("group-3");
let group4 = document.getElementById("group-4");
let group5 = document.getElementById("group-5");
let group6 = document.getElementById("group-6");
let group7 = document.getElementById("group-7");
let group8 = document.getElementById("group-8");
let group9 = document.getElementById("group-9");
let group10 = document.getElementById("group-10");
let group11 = document.getElementById("group-11");
let group12 = document.getElementById("group-12");
let group13 = document.getElementById("group-13");
let group14 = document.getElementById("group-14");
let group_winner = document.getElementById("group-winner");

let line_a = document.getElementById("line-a");
let line_b = document.getElementById("line-b");
let line_c = document.getElementById("line-c");
let line_d = document.getElementById("line-d");
let line_e = document.getElementById("line-e");
let line_f = document.getElementById("line-f");
let line_g = document.getElementById("line-g");
let line_h = document.getElementById("line-h");
let line_i = document.getElementById("line-i");
let line_j = document.getElementById("line-j");
let line_k = document.getElementById("line-k");
let line_l = document.getElementById("line-l");
let line_m = document.getElementById("line-m");
let line_n = document.getElementById("line-n");
let line_o = document.getElementById("line-o");
let line_p = document.getElementById("line-p");
let line_q = document.getElementById("line-q");
let line_r = document.getElementById("line-r");
let line_s = document.getElementById("line-s");
let line_t = document.getElementById("line-t");
let line_z = document.getElementById("line-z");

function select() {
    for(let i = 0; i < arguments.length; i++) {
        arguments[i].style.borderColor = "#0a5bff";
    }
}

function back() {
    for(let i = 0; i < arguments.length; i++) {
        arguments[i].style.borderColor = "#c4c4c4";
    }
}

group1.addEventListener("mouseover", function() {
    select(line_z, group_winner);
    select(group1, group5, group7);
    select(line_a, line_b, line_g, line_h, line_j);
});

group1.addEventListener("mouseout", function() {
    back(line_z, group_winner);
    back(group1, group5, group7);
    back(line_a, line_b, line_g, line_h, line_j);
});

group2.addEventListener("mouseover", function() {
    select(line_z, group_winner);
    select(group2, group5, group7);
    select(line_c, line_b, line_g, line_h, line_j);
});

group2.addEventListener("mouseout", function() {
    back(line_z, group_winner);
    back(group2, group5, group7);
    back(line_c, line_b, line_g, line_h, line_j);
});

group3.addEventListener("mouseover", function() {
    select(line_z, group_winner);
    select(group3, group6, group7);
    select(line_d, line_e, line_i, line_h, line_j);
});

group3.addEventListener("mouseout", function() {
    back(line_z, group_winner);
    back(group3, group6, group7);
    back(line_d, line_e, line_i, line_h, line_j);
});

group4.addEventListener("mouseover", function() {
    select(line_z, group_winner);
    select(group4, group6, group7);
    select(line_f, line_e, line_i, line_h, line_j);
});

group4.addEventListener("mouseout", function() {
    back(line_z, group_winner);
    back(group4, group6, group7);
    back(line_f, line_e, line_i, line_h, line_j);
});

group8.addEventListener("mouseover", function() {
    select(line_z, group_winner);
    select(group8, group12, group14);
    select(line_k, line_l, line_q, line_r, line_t);
});

group8.addEventListener("mouseout", function() {
    back(line_z, group_winner);
    back(group8, group12, group14);
    back(line_k, line_l, line_q, line_r, line_t);
});

group9.addEventListener("mouseover", function() {
    select(line_z, group_winner);
    select(group9, group12, group14);
    select(line_m, line_l, line_q, line_r, line_t);
});

group9.addEventListener("mouseout", function() {
    back(line_z, group_winner);
    back(group9, group12, group14);
    back(line_m, line_l, line_q, line_r, line_t);
});

group10.addEventListener("mouseover", function() {
    select(line_z, group_winner);
    select(group10, group13, group14);
    select(line_n, line_o, line_s, line_r, line_t);
});

group10.addEventListener("mouseout", function() {
    back(line_z, group_winner);
    back(group10, group13, group14);
    back(line_n, line_o, line_s, line_r, line_t);
});

group11.addEventListener("mouseover", function() {
    select(line_z, group_winner);
    select(group11, group13, group14);
    select(line_p, line_o, line_s, line_r, line_t);
});

group11.addEventListener("mouseout", function() {
    back(line_z, group_winner);
    back(group11, group13, group14);
    back(line_p, line_o, line_s, line_r, line_t);
});