// ELEMENT IDs
const OTP_FORM_CONTAINER_ID = '#otp_container';
const REG_FORM_CONTAINER_ID = '#registration_form_container';
const CSRF_INPUT_ID = '#csrf_token';
const SEND_OTP_BTN_ID = '#send_otp_btn';
const OTP_INPUT_CONTAINER_ID = '#otp_input_container';
const VERIFY_OTP_BTN_ID = '#verify_otp_btn';
const ALERT_CONTAINER_ID = '#alert_container';
const STEPS_CONTAINER_ID = '#steps_container';
const CLIENT_REF_CONTAINER_ID = '#step_3';
const ADD_MORE_CLIENT_BTN_ID = '#add_client_reference';
const NEXT_BTN_ID = '#next_btn';
const PREV_BTN_ID = '#prev_btn';
const SUBMIT_BTN_ID = '#submit_btn';
const DECLARATION_CHECKBOX_ID = '#declarationCheckbox';
const MODAL_1 = 'modal_1';
// API Endpoints
const SEND_OTP_API = '/supplies/register/send-otp';
const VERIFY_OTP_API = '/supplies/register/verify-otp';
const SUBMIT_FORM_API = '/supplies/register/submit';


function get_csrf_token() {
    return $(CSRF_INPUT_ID).val();
}

const pageManager = {
    totalSteps: 5,
    page: 1,
    email: '',
    otp: '',
    data: {},
    goNext: function () {
        if (this.page < this.totalSteps) {
            this.page += 1;
            this.showStep();
        }
        return this.page;
    },
    goBack: function () {
        if (this.page > 1) {
            this.page -= 1;
            this.showStep();
        }
        return this.page;
    },
    showStep: function () {
        $(`${STEPS_CONTAINER_ID} .step`).each((index, element) => {
            if (index + 1 === this.page) {
                $(element).show();
            } else {
                $(element).hide();
            }
        });
        if (this.page === 1) {
            $(PREV_BTN_ID).hide();
        } else {
            $(PREV_BTN_ID).show();
        }
        if (this.page === this.totalSteps) {
            $(NEXT_BTN_ID).hide();
            $(SUBMIT_BTN_ID).show();
        } else {
            $(NEXT_BTN_ID).show();
            $(SUBMIT_BTN_ID).hide();
        }

    },
    getRegData: function () {
        const data = {};
        $(REG_FORM_CONTAINER_ID).find('input, select').each((index, element) => {
            let name = $(element).attr('name');
            let type = $(element).attr('type');
            if (!name) {
                return;
            }
            if (type === 'file') {
                const files = element.files;
                if (files && files.length) {
                    // If the input allows multiple files
                    if ($(element).prop('multiple')) {
                        // Convert FileList to an array.
                        data[name] = Array.from(files);
                    } else {
                        // Otherwise, store the first file.
                        data[name] = files[0];
                    }
                }
            } else {
                let value = $(element).val();
                if (value) {
                    data[name] = value;
                }
            }
        });
        return data;
    },
    getFormData: function () {
        const formData = new FormData();
        const regData = this.getRegData();
        
        for (const key in regData) {
            console.log(key, regData[key]);
            if (Array.isArray(regData[key])) {
                regData[key].forEach((file, index) => {
                    formData.append(`${key}_${index}`, file);
                });
            } else {
                formData.append(key, regData[key]);
            }
        }
        const csrf_token = get_csrf_token();
        formData.append('csrf_token', csrf_token);
        formData.append('email', this.email);
        formData.append('otp', this.otp);
        return formData;        
    }, 
    handleSubmitForm: function (handler) {
        if (typeof handler !== 'function') {
            return;
        }
        if (this.page !== this.totalSteps) {
            return;
        }
        const formData = this.getFormData();        
        handler(formData);
    }
}

function showModal(id, body_content=null, static_backdrop=false, hide_close_btn=false) {
    if (body_content) {
        $(`#${id} .modal-body`).html(body_content);
    }
    if (static_backdrop) {
        $(`#${id}`).attr('data-bs-backdrop', 'static');
    } else {
        $(`#${id}`).removeAttr('data-bs-backdrop');
    }
    if (hide_close_btn) {
        $(`#${id} .modal-header .btn-close`).hide();
    } else {
        $(`#${id} .modal-header .btn-close`).show();
    }
    const elem = document.getElementById(id)
    const mBootstrap = new bootstrap.Modal(elem);
    mBootstrap.show()
}

function showError(alertContainerId, msg) {
    $(alertContainerId).removeClass("alert-warning");
    $(alertContainerId).addClass("alert-danger");
    $(`${alertContainerId} .error_message_text`).text(msg)
    $(alertContainerId).show(200,()=>{
        setTimeout(()=>{
            $(alertContainerId).hide()
        }, 20000)
    })
}

function showWarning(alertContainerId, msg) {
    $(alertContainerId).removeClass("alert-danger");
    $(alertContainerId).addClass("alert-warning");
    $(`${alertContainerId} .error_message_text`).text(msg)
    $(alertContainerId).show(200,()=>{
        setTimeout(()=>{
            $(alertContainerId).hide(200)
        }, 20000)
    })
}

function showToast() {
    const toastLiveExample = document.getElementById('liveToast')
    const toastBootstrap = bootstrap.Toast.getOrCreateInstance(toastLiveExample)
    toastBootstrap.show()
}

function validateStepInputs(step) {
    let isValid = true;
    const toggleIsInvalid = (element, isInvalid) => {
        if (isInvalid) {
            $(element).addClass('is-invalid');
            isValid = false;            
        } else {    
            $(element).removeClass('is-invalid');
        }
        return isInvalid;
    }
    // Check all input fields of the step
    $(`#step_${step} input`).each((index, element) => {
        // skip file input
        if ($(element).attr('type') === 'file') {
            return;
        }
        // first check if the input is required
        if ($(element).attr('required')) {
            let notValid = toggleIsInvalid(element, !$(element).val());
            if (notValid) {
                if (!$(element).next().hasClass('invalid-feedback')) {
                    $('<div class="invalid-feedback">This field is required</div>').insertAfter($(element));
                }
            } else {
                if ($(element).next().hasClass('invalid-feedback')) {
                    $(element).next().remove();
                }
            }
        }
        // check for pattern
        if ($(element).attr('pattern')) {
            const pattern = new RegExp($(element).attr('pattern'));
            toggleIsInvalid(element, !pattern.test($(element).val()));
        }
        // validate date input min and max set
        if ($(element).attr('type') === 'date' && $(element).val()) {
            const min = $(element).attr('min');
            const max = $(element).attr('max');
            if (min) {
                toggleIsInvalid(element, $(element).val() < min);
            }
            if (max) {
                toggleIsInvalid(element, $(element).val() > max);
            }
        }
    });
    // Check dependent fields
    // First it catches all the fields which is required if some other field is filled. Their classes are set on the data attribute "data-requires-if"
    // Then it checks from the `data-container-class` of the dependent field for the required fields.
    $(`#step_${step} input[data-requires-if]`).each((index, element) => {
        const dependentField = $(element);
        if (dependentField.val()) {
            toggleIsInvalid(element, false);
            return;
        }
        const requiredFieldClasses = dependentField.data('requires-if').split(',');
        const parent = dependentField.closest(`.${dependentField.data('container-class')}`);
        let requiredFields = parent.find(
            requiredFieldClasses.map((className) => `.${className}`).join(',')
        )
        console.log(typeof requiredFields);
        const any_field_filled = requiredFields.map((index, field) => $(field).val().length > 0).get().some((val) => val);
        toggleIsInvalid(element, any_field_filled);
    });
    return isValid;
}

function isValidEmail(email) {
    const emailPattern = /^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,6}$/;
    return emailPattern.test(email);
}

function addMoreClientReference() {
    const total_clients = $(`${CLIENT_REF_CONTAINER_ID} .client`).length;
    const visible_clients = $(`${CLIENT_REF_CONTAINER_ID} .client`).filter(function () {
        return $(this).css("display") !== "none";
    }).length;
    // show the next client with display=none if visible clients are less than total clients
    if (visible_clients < total_clients) {
        $(`${CLIENT_REF_CONTAINER_ID} .client`).each(function () {
            if ($(this).css("display") === "none") {
                $(this).show();
                return false;
            }
        });
        if (visible_clients + 1 === total_clients) {
            $(ADD_MORE_CLIENT_BTN_ID).hide();
        }
    }
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
            if (data?.result?.status === 'success') {
                showWarning(ALERT_CONTAINER_ID, 'OTP has been sent to your email.');
                $(SEND_OTP_BTN_ID).hide();
                $(OTP_INPUT_CONTAINER_ID).show(
                    200,
                    () => {
                        $(`${OTP_INPUT_CONTAINER_ID} input`).focus();
                    }
                );
                $(VERIFY_OTP_BTN_ID).show();
                $('#email').prop('readonly', true);
            } else {
                showError(ALERT_CONTAINER_ID, data?.result?.message || 'Failed to send OTP');
            }
        },
        error: function (xhr, status, error) {
            showError(ALERT_CONTAINER_ID, 'Failed to send OTP');
        },
        complete: function () {
            $(SEND_OTP_BTN_ID).prop('disabled', false);
        },
    });
}

function verify_otp() {
    const email = $('#email').val();
    const otp = $('#otp').val();
    if (!otp) {
        showError(ALERT_CONTAINER_ID, 'OTP is required');
        return;
    }
    $.ajax({
        type: 'POST',
        url: VERIFY_OTP_API,
        contentType: 'application/json',
        dataType: 'json',
        beforeSend: function (xhr) {
            xhr.setRequestHeader('X-CSRFToken', get_csrf_token());
            $(VERIFY_OTP_BTN_ID).prop('disabled', true);
        },
        data: JSON.stringify(format_rpc_data({email: email, otp: otp})),
        success: function (data) {
            if (data?.result?.status === 'success') {
                showWarning(ALERT_CONTAINER_ID, 'OTP verified. Proceeding to registration.');
                setTimeout(() => {
                    $(OTP_FORM_CONTAINER_ID).hide(200, () => {
                        $(REG_FORM_CONTAINER_ID).show(200);
                        pageManager.email = email;
                        pageManager.otp = otp;
                    });
                }, 1500);
            } else {
                const error_msg = data?.result?.message || 'Invalid OTP. Please try again.';
                showError(ALERT_CONTAINER_ID, error_msg);
            }
        },
        error: function (xhr, status, error) {
            console.log(xhr, status, error);
            showError(ALERT_CONTAINER_ID, 'Invalid OTP. Please try again.');
        },
        complete: function () {
            $(VERIFY_OTP_BTN_ID).prop('disabled', false);
        },
    });
}

function submit_form(formData) {
    $.ajax({
        type: 'POST',
        url: SUBMIT_FORM_API,
        contentType: false,
        processData: false,
        beforeSend: function () {
            $(SUBMIT_BTN_ID).prop('disabled', true);
        },
        data: formData,
        success: function (data) {
            console.log(data);
            if (data?.status === 'success') {
                showModal(
                    MODAL_1,
                    data?.data?.html || 'Form submitted successfully',
                    true,
                    true
                );
            } else {
                showModal(MODAL_1, data?.data?.html || 'Failed to submit form', true);
            }
        },
        error: function (xhr, status, error) {
            showModal(
                MODAL_1,
                "<div class='alert alert-danger my-4'>Failed to submit form</div>",
            )
        },
        complete: function () {
            $(SUBMIT_BTN_ID).prop('disabled', false);
        },
    });
}

$(document).ready(function () {
    $(SEND_OTP_BTN_ID).on('click', send_otp);
    $(VERIFY_OTP_BTN_ID).on('click', verify_otp);
    $(NEXT_BTN_ID).on('click', () => {
        console.log('Next Button Clicked');
        pageManager.goNext();
    });
    $(PREV_BTN_ID).on('click', () => {
        pageManager.goBack();
    });
    $(ADD_MORE_CLIENT_BTN_ID).on('click', addMoreClientReference);
    $(SUBMIT_BTN_ID).on('click', () => {
        pageManager.handleSubmitForm(submit_form);
    });
    $(DECLARATION_CHECKBOX_ID).on('change', function () {
        const isChecked = $(this).is(':checked');
        $(SUBMIT_BTN_ID).prop('disabled', !isChecked);
    });
});