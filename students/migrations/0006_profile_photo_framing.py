from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("students", "0005_requeue_approved_profiles_missing_gender")]

    operations = [
        migrations.AddField(model_name="profile", name="photo_position_x", field=models.PositiveSmallIntegerField(default=50)),
        migrations.AddField(model_name="profile", name="photo_position_y", field=models.PositiveSmallIntegerField(default=50)),
        migrations.AddField(model_name="profile", name="photo_scale", field=models.PositiveSmallIntegerField(default=100)),
    ]
