// ELEMENT IDs
const CSRF_INPUT_ID = '#csrf_token';
const SEND_OTP_BTN_ID = '#send_otp_btn';
const VERIFY_OTP_BTN_ID = '#verify_otp_btn';
const ALERT_CONTAINER_ID = '#alert_container';

// API Endpoints
const SEND_OTP_API = '/supplier-registration/send-otp';

function showError(alertContainerId, msg) {
    $(alertContainerId).removeClass("alert-warning");
    $(alertContainerId).addClass("alert-danger");
    $(`${alertContainerId} .error_message_text`).text(msg)
    $(alertContainerId).show(200,()=>{
        setTimeout(()=>{
            $(alertContainerId).hide()
        }, 2000)
    })
}

function showWarning(alertContainerId, msg) {
    $(alertContainerId).removeClass("alert-danger");
    $(alertContainerId).addClass("alert-warning");
    $(`${alertContainerId} .error_message_text`).text(msg)
    $(alertContainerId).show(200,()=>{
        setTimeout(()=>{
            $(alertContainerId).hide(200)
        }, 2000)
    })
}

function isValidEmail(email) {
    const emailPattern = /^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,6}$/;
    return emailPattern.test(email);
}

function get_csrf_token() {
    return $(CSRF_INPUT_ID).val();
}

function format_rpc_data(data) {
    return {
        jsonrpc: '2.0',
        method: 'call',
        params: data,
    };
}

function send_otp() {
    const email = $('#email').val();
    if (!isValidEmail(email)) {
        showError(ALERT_CONTAINER_ID, 'Invalid Email');
        return;
    }
    $.ajax({
        type: 'POST',
        url: SEND_OTP_API,
        contentType: 'application/json',
        dataType: 'json',
        beforeSend: function (xhr) {
            xhr.setRequestHeader('X-CSRFToken', get_csrf_token());
            $(SEND_OTP_BTN_ID).prop('disabled', true);
        },
        data: JSON.stringify(format_rpc_data({email: email})),
        success: function (data) {
            console.log(data);
        },
        error: function (xhr, status, error) {
            showError(ALERT_CONTAINER_ID, 'Failed to send OTP');
        }
    });
}

$(document).ready(function () {
    $(SEND_OTP_BTN_ID).on('click', send_otp);
});
