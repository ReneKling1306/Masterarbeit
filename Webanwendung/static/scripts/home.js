var first_next = document.querySelectorAll(".first_next");
var main_form = document.querySelectorAll(".main");
var step_list = document.querySelectorAll(".progress-bar li");
var num = document.querySelector(".step-number");
let formnumber = 0;
var next_button = document.querySelectorAll(".next_button");
var form_quick = document.querySelector("#radio_yes");
var shownname = document.querySelector(".shown_name");



first_next.forEach(function (next_click_form) {
    next_click_form.addEventListener('click', function () {
        if (!validateform()) {
            return false
        }
        console.log(formnumber);
        console.log(form_quick.checked);
        if(form_quick.checked) {
            formnumber++;
            $('#content').show()
        } else {
            formnumber++;
            
        }
        updateform();
        progress_forward();
    });
});

next_button.forEach(function (next_click_form) {
    next_click_form.addEventListener('click', function () {
        if (!validateform()) {
            return false
        }
        console.log(formnumber);
        console.log(form_quick.checked);
        if(form_quick.checked) {
            formnumber++;
            $('#content').show()
        } else {
            formnumber++;
            
        }
        updateform();
        progress_forward();
    });
});


var back_click = document.querySelectorAll(".back_button");
back_click.forEach(function (back_click_form) {
    back_click_form.addEventListener('click', function () {
        formnumber--;
        updateform();
        progress_backward();
    });
});

var submit_click = document.querySelectorAll(".submit_button");
submit_click.forEach(function (submit_click_form) {
    submit_click_form.addEventListener('click', function () {
        shownname.innerHTML = username.value;
        formnumber++;
        updateform();
    });
});

function updateform() {
    main_form.forEach(function (mainform_number) {
        mainform_number.classList.remove('active');
    })
    main_form[formnumber].classList.add('active');
}

function updateform_quick() {
    main_form.forEach(function (mainform_number) {
        mainform_number.classList.remove('active');
    })
    main_form[formnumber].classList.add('active');
}

function progress_forward() {
    // step_list.forEach(list => {

    //     list.classList.remove('active');

    // }); 


    num.innerHTML = formnumber + 1;
    step_list[formnumber].classList.add('active');
}

function progress_backward() {
    var form_num = formnumber + 1;
    step_list[form_num].classList.remove('active');
    num.innerHTML = form_num;
}

function validateform() {
    validate = true;
    var validate_inputs = document.querySelectorAll(".main.active input");
    validate_inputs.forEach(function (vaildate_input) {
        vaildate_input.classList.remove('warning');
        if (vaildate_input.hasAttribute('require')) {
            if (vaildate_input.value.length == 0) {
                validate = false;
                vaildate_input.classList.add('warning');
            }
        }
    });
    return validate;

}