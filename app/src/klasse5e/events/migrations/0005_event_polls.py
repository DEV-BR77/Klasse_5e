import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("events", "0004_reservation_fulfilled_at")]
    operations = [
        migrations.CreateModel(name="EventPoll", fields=[("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")), ("title", models.CharField(max_length=200)), ("description", models.TextField(blank=True)), ("closes_at", models.DateTimeField()), ("created_at", models.DateTimeField(auto_now_add=True)), ("created_by", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)), ("finalized_event", models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="source_poll", to="events.event")), ("school_class", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="core.schoolclass"))]),
        migrations.CreateModel(name="EventPollOption", fields=[("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")), ("starts_at", models.DateTimeField()), ("ends_at", models.DateTimeField()), ("poll", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="options", to="events.eventpoll"))], options={"ordering": ["starts_at"]}),
        migrations.CreateModel(name="EventPollVote", fields=[("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")), ("created_at", models.DateTimeField(auto_now_add=True)), ("option", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="votes", to="events.eventpolloption")), ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL))]),
        migrations.AddConstraint(model_name="eventpollvote", constraint=models.UniqueConstraint(fields=("option", "user"), name="unique_event_poll_vote")),
    ]
