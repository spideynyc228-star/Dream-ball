from django.db import migrations


def requeue_incomplete_approved_profiles(apps, schema_editor):
    Profile = apps.get_model("students", "Profile")
    Profile.objects.filter(status="approved", gender="").update(status="pending")


class Migration(migrations.Migration):
    dependencies = [
        ("students", "0004_profile_gender"),
    ]

    operations = [
        migrations.RunPython(requeue_incomplete_approved_profiles, migrations.RunPython.noop),
    ]
