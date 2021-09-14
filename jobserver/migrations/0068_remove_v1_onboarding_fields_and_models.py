# Generated by Django 3.2.5 on 2021-09-14 13:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("jobserver", "0067_alter_org_github_orgs"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="project",
            name="data_access_legal_basis",
        ),
        migrations.RemoveField(
            model_name="project",
            name="description",
        ),
        migrations.RemoveField(
            model_name="project",
            name="email",
        ),
        migrations.RemoveField(
            model_name="project",
            name="ethics_approval",
        ),
        migrations.RemoveField(
            model_name="project",
            name="evidence_of_scripting_languages",
        ),
        migrations.RemoveField(
            model_name="project",
            name="evidence_of_sharing_in_public",
        ),
        migrations.RemoveField(
            model_name="project",
            name="funding_source",
        ),
        migrations.RemoveField(
            model_name="project",
            name="governance_approval_notes",
        ),
        migrations.RemoveField(
            model_name="project",
            name="has_governance_approval",
        ),
        migrations.RemoveField(
            model_name="project",
            name="has_signed_declaration",
        ),
        migrations.RemoveField(
            model_name="project",
            name="has_technical_approval",
        ),
        migrations.RemoveField(
            model_name="project",
            name="is_research_on_cmo_priority_list",
        ),
        migrations.RemoveField(
            model_name="project",
            name="job_title",
        ),
        migrations.RemoveField(
            model_name="project",
            name="next_step",
        ),
        migrations.RemoveField(
            model_name="project",
            name="previous_experience_with_ehr",
        ),
        migrations.RemoveField(
            model_name="project",
            name="project_lead",
        ),
        migrations.RemoveField(
            model_name="project",
            name="proposed_duration",
        ),
        migrations.RemoveField(
            model_name="project",
            name="proposed_start_date",
        ),
        migrations.RemoveField(
            model_name="project",
            name="purpose",
        ),
        migrations.RemoveField(
            model_name="project",
            name="region",
        ),
        migrations.RemoveField(
            model_name="project",
            name="requested_data_meets_purpose",
        ),
        migrations.RemoveField(
            model_name="project",
            name="satisfying_confidentiality",
        ),
        migrations.RemoveField(
            model_name="project",
            name="team_details",
        ),
        migrations.RemoveField(
            model_name="project",
            name="team_name",
        ),
        migrations.RemoveField(
            model_name="project",
            name="technical_approval_notes",
        ),
        migrations.RemoveField(
            model_name="project",
            name="telephone",
        ),
        migrations.RemoveField(
            model_name="project",
            name="why_data_is_required",
        ),
        migrations.RemoveField(
            model_name="project",
            name="researcher_registrations",
        ),
        migrations.DeleteModel(
            name="ResearcherRegistration",
        ),
    ]
