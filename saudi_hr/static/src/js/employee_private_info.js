odoo.define('saudi.employee_private_info', function (require) {
'use strict';

var publicWidget = require('web.public.widget');

publicWidget.registry.employee_private_info = publicWidget.Widget.extend({
    selector: '.employee_private_info',
    events: {
        'click .qualification_add_a_line': 'onClickQualificationAddLine',
        'click .certification_add_a_line': 'onClickCertificationAddLine',
        'click .experience_add_a_line': 'onClickExperienceAddLine',
        'click .save_qualification': 'onClickSaveQualification',
        'click .save_certification': 'onClickSaveCertification',
        'click .save_experience': 'onClickSaveExperience'
    },

    onClickQualificationAddLine: function(ev) {
        $('#qualificationAddLine').modal('show');
    },

    onClickCertificationAddLine: function(ev) {
        $('#certificationAddLine').modal('show');
    },

    onClickExperienceAddLine: function(ev) {
        $('#ExperienceAddLine').modal('show');
    },

    onClickSaveQualification: function(ev) {
        var qualificationBody = $('.qualification_body');
        var qualificationUniversityName = $('.qualification-university-name')[0].value;
        var qualificationProgram = $('.qualification-program').find(':selected').val();
        var qualificationProgramText = $('.qualification-program').find(':selected').text();
        var qualificationContactName = $('.qualification-contact-name')[0].value;
        var qualificationContactEmail = $('.qualification-contact-email')[0].value;
        var qualificationProgramStatus = $('.qualification-program-status').find(':selected').val();
        var qualificationProgramStatusText = $('.qualification-program-status').find(':selected').text();
        var qualificationPhone = $('.qualification-phone')[0].value;
        var qualificationProgramMonth = $('.qualification-program-month').find(':selected').val();
        var qualificationProgramMonthText = $('.qualification-program-month').find(':selected').text();
        var qualificationYear = $('.qualification-year')[0].value;
        var qualificationActivitiesSocieties = $('.qualification-activities-societies')[0].value;
        var qualificationDescription = $('.qualification-description')[0].value;
        // var qualificationDescription = $('.qualification-activities-societies')[0].value;
        // var qualificationDescription = $('.qualification-description')[0].value;
        var qualificationTr = qualificationBody.find('tr');
        var new_tr = $(`<tr id="witness_tr_${parseInt(qualificationTr.length)}">
                <td><input type="hidden" name="qualification_tr_${parseInt(qualificationTr.length)}_university_id" value="${qualificationUniversityName}" />${qualificationUniversityName}</td>
                <td><input type="hidden" name="qualification_tr_${parseInt(qualificationTr.length)}_program_type" value="${qualificationProgramStatus}" />${qualificationProgramStatusText}</td>
                <td><input type="hidden" name="qualification_tr_${parseInt(qualificationTr.length)}_degree_id" value="${qualificationProgram}" />${qualificationProgramText}</td>
                <td><input type="hidden" name="qualification_tr_${parseInt(qualificationTr.length)}_completion_month" value="${qualificationProgramMonth}" />${qualificationProgramMonthText}</td>
                <td><input type="hidden" name="qualification_tr_${parseInt(qualificationTr.length)}_completion_year" value="${qualificationYear}" />${qualificationYear}</td>
                <td><input type="hidden" name="qualification_tr_${parseInt(qualificationTr.length)}_contact_name" value="${qualificationContactName}" />${qualificationContactName}</td>
                <td><input type="hidden" name="qualification_tr_${parseInt(qualificationTr.length)}_contact_phone" value="${qualificationPhone}" />${qualificationPhone}</td>
                <td><input type="hidden" name="qualification_tr_${parseInt(qualificationTr.length)}_contact_email" value="${qualificationContactEmail}" />${qualificationContactEmail}</td>
                <td><input type="hidden" name="qualification_tr_${parseInt(qualificationTr.length)}_activities" value="${qualificationActivitiesSocieties}" />${qualificationActivitiesSocieties}</td>
                <td><input type="hidden" name="qualification_tr_${parseInt(qualificationTr.length)}_description" value="${qualificationDescription}" />${qualificationDescription}</td>
            </tr>`);
        $('.qualification_add_line_row').before(new_tr);
        $('.qualification-university-name').val('');
        $('.qualification-program').prop('selected', false);
        $('.qualification-contact-name').val('');
        $('.qualification-contact-email').val('');
        $('.qualification-program-status').prop('selected', false);
        $('.qualification-phone').val('');
        $('.qualification-program-month').prop('selected', false);
        $('.qualification-year').val('');
        $('.qualification-activities-societies').val('');
        $('.qualification-description').val('');
        $('#qualificationAddLine').modal('hide');
    },

    onClickSaveCertification: function(ev) {
        var certificationBody = $('.certification_body');
        var certificationName = $('.certification-certification-name')[0].value;
        var certificationIssuingOrganization = $('.certification-issuing-organization')[0].value;
        var certificationDateOfIssue = $('.certification-date-of-issue')[0].value;
        var certificationDateOfExpiry = $('.certification-date-of-expiry')[0].value;
        var certificationRegistration = $('.certification-registration')[0].value;
        var certificationCotactName = $('.certification-contact-name')[0].value;
        var certificationContactPhone = $('.certification-contact-phone')[0].value;
        var certificationCotactEmail = $('.certification-contact-email')[0].value;
        var certificationTr = certificationBody.find('tr');
        var new_tr = $(`<tr id="witness_tr_${parseInt(certificationTr.length)}">
                <td><input type="hidden" name="certification_tr_${parseInt(certificationTr.length)}_name" value="${certificationName}" />${certificationName}</td>
                <td><input type="hidden" name="certification_tr_${parseInt(certificationTr.length)}_organization_name" value="${certificationIssuingOrganization}" />${certificationIssuingOrganization}</td>
                <td><input type="hidden" name="certification_tr_${parseInt(certificationTr.length)}_issue_date" value="${certificationDateOfIssue}" />${certificationDateOfIssue}</td>
                <td><input type="hidden" name="certification_tr_${parseInt(certificationTr.length)}_expiry_date" value="${certificationDateOfExpiry}" />${certificationDateOfExpiry}</td>
                <td><input type="hidden" name="certification_tr_${parseInt(certificationTr.length)}_reg_no" value="${certificationRegistration}" />${certificationRegistration}</td>
                <td><input type="hidden" name="certification_tr_${parseInt(certificationTr.length)}_contact_name" value="${certificationCotactName}" />${certificationCotactName}</td>
                <td><input type="hidden" name="certification_tr_${parseInt(certificationTr.length)}_contact_phone" value="${certificationContactPhone}" />${certificationContactPhone}</td>
                <td><input type="hidden" name="certification_tr_${parseInt(certificationTr.length)}_contact_email" value="${certificationCotactEmail}" />${certificationCotactEmail}</td>
            </tr>`);
        $('.certification_add_line_row').before(new_tr);
        $('.certification-certification-name').val('');
        $('.certification-issuing-organization').val('');
        $('.certification-date-of-issue').val('');
        $('.certification-date-of-expiry').val('');
        $('.certification-registration').val('');
        $('.certification-contact-name').val('');
        $('.certification-contact-phone').val('');
        $('.certification-contact-email').val('');
        $('#certificationAddLine').modal('hide');
    },

    onClickSaveExperience: function(ev) {
        var experienceBody = $('.experience_body');
        var experienceCurrentJob = $('.experience-current-job').find(':selected').val();
        var experienceCurrentJobText = $('.experience-current-job').find(':selected').text();
        var experienceContactName = $('.experience-contact-name')[0].value;
        var experienceCompanyName = $('.experience-company-name')[0].value;
        var experienceContactPhone = $('.experience-contact-phone')[0].value;
        var experienceJobTitle = $('.experience-job-title')[0].value;
        var experienceContactEmail = $('.experience-contact-email')[0].value;
        var experienceLocation = $('.experience-location')[0].value;
        var experienceContactTitle = $('.experience-contact-title')[0].value;
        var experienceTimePeriodFrom = $('.experience-time-period-from')[0].value;
        var experienceTimePeriodTo = $('.experience-time-period-to')[0].value;
        var experienceDescription = $('.experience-description')[0].value;
        var experienceTr = experienceBody.find('tr');
        var new_tr = $(`<tr id="witness_tr_${parseInt(experienceTr.length)}">
                <td><input type="hidden" name="experience_tr_${parseInt(experienceTr.length)}_is_current_job" value="${experienceCurrentJob}" />${experienceCurrentJobText}</td>
                <td><input type="hidden" name="experience_tr_${parseInt(experienceTr.length)}_company" value="${experienceCompanyName}" />${experienceCompanyName}</td>
                <td><input type="hidden" name="experience_tr_${parseInt(experienceTr.length)}_job_title" value="${experienceJobTitle}" />${experienceJobTitle}</td>
                <td><input type="hidden" name="experience_tr_${parseInt(experienceTr.length)}_location" value="${experienceLocation}" />${experienceLocation}</td>
                <td><input type="hidden" name="experience_tr_${parseInt(experienceTr.length)}_time_period_from" value="${experienceTimePeriodFrom}" />${experienceTimePeriodFrom}</td>
                <td><input type="hidden" name="experience_tr_${parseInt(experienceTr.length)}_time_period_to" value="${experienceTimePeriodTo}" />${experienceTimePeriodTo}</td>
                <td><input type="hidden" name="experience_tr_${parseInt(experienceTr.length)}_contact_name" value="${experienceContactName}" />${experienceContactName}</td>
                <td><input type="hidden" name="experience_tr_${parseInt(experienceTr.length)}_contact_phone" value="${experienceContactPhone}" />${experienceContactPhone}</td>
                <td><input type="hidden" name="experience_tr_${parseInt(experienceTr.length)}_contact_email" value="${experienceContactEmail}" />${experienceContactEmail}</td>
                <td><input type="hidden" name="experience_tr_${parseInt(experienceTr.length)}_contact_title" value="${experienceContactTitle}" />${experienceContactTitle}</td>
                <td><input type="hidden" name="experience_tr_${parseInt(experienceTr.length)}_description" value="${experienceDescription}" />${experienceDescription}</td>
            </tr>`);
        $('.experience_add_line_row').before(new_tr);
        $('.experience-current-job').prop('selected', false);
        $('.experience-contact-name').val('');
        $('.experience-company-name').val('');
        $('.experience-contact-phone').val('');
        $('.experience-job-title').val('');
        $('.experience-contact-email').val('');
        $('.experience-location').val('');
        $('.experience-contact-title').val('');
        $('.experience-time-period-from').val('');
        $('.experience-time-period-to').val('');
        $('.experience-description').val('');
        $('#ExperienceAddLine').modal('hide');
    }

});
});
