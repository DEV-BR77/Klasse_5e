from datetime import date, time

import pytest
from django.core.exceptions import ValidationError

from klasse5e.schedule.models import LessonPeriod, SchoolBreak, TimeGrid


@pytest.mark.django_db
def test_lesson_period_and_break_validation(school):
    grid = TimeGrid.objects.create(school=school, name="Regelplan", valid_from=date(2026, 8, 1))
    first = LessonPeriod.objects.create(time_grid=grid, number=1, starts_at=time(8), ends_at=time(8, 45))
    first.full_clean()
    invalid = LessonPeriod(time_grid=grid, number=2, starts_at=time(8, 30), ends_at=time(9, 15))
    with pytest.raises(ValidationError, match="überschneiden"):
        invalid.full_clean()
    backwards = SchoolBreak(time_grid=grid, label="Pause", after_period=1, starts_at=time(9), ends_at=time(8, 50))
    with pytest.raises(ValidationError, match="nach ihrem Beginn"):
        backwards.full_clean()
