from django.db import models


class MealPlan(models.Model):
    class Status(models.TextChoices):
        READY = "ready", "Veröffentlicht"
        REVIEW = "review", "Prüfung nötig"
        FAILED = "failed", "Abruf fehlgeschlagen"

    source_id = models.CharField(max_length=180, unique=True)
    iso_year = models.PositiveSmallIntegerField()
    iso_week = models.PositiveSmallIntegerField()
    starts_on = models.DateField()
    ends_on = models.DateField()
    source_url = models.URLField(max_length=1200)
    checksum = models.CharField(max_length=64)
    document_version = models.CharField(max_length=80, blank=True)
    legend = models.JSONField(default=dict, blank=True)
    status = models.CharField(max_length=16, choices=Status, default=Status.REVIEW)
    parser_version = models.CharField(max_length=24, default="position-v1")
    fetched_at = models.DateTimeField(auto_now=True)
    error_code = models.CharField(max_length=80, blank=True)

    class Meta:
        ordering = ["starts_on"]


class MealDay(models.Model):
    plan = models.ForeignKey(MealPlan, on_delete=models.CASCADE, related_name="days")
    date = models.DateField()
    is_published = models.BooleanField(default=True)

    class Meta:
        ordering = ["date"]
        constraints = [models.UniqueConstraint(fields=["plan", "date"], name="unique_meal_day")]


class MealOption(models.Model):
    day = models.ForeignKey(MealDay, on_delete=models.CASCADE, related_name="options")
    line = models.PositiveSmallIntegerField()
    components = models.JSONField(default=list)
    additive_codes = models.JSONField(default=list, blank=True)
    allergen_codes = models.JSONField(default=list, blank=True)

    class Meta:
        ordering = ["line"]
        constraints = [models.UniqueConstraint(fields=["day", "line"], name="unique_meal_option")]
