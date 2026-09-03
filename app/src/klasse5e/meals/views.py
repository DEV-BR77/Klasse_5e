from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils import timezone

from klasse5e.core.policies import active_class_for_user

from .models import MealPlan


@login_required
def meal_plans(request):
    active_class_for_user(request.user)
    today = timezone.localdate()
    plans = MealPlan.objects.filter(
        status=MealPlan.Status.READY, ends_on__gte=today
    ).prefetch_related("days__options")[:6]
    return render(
        request,
        "meals/plans.html",
        {
            "page_title": "Speiseplan",
            "active_section": "more",
            "plans": plans,
            "today": today,
        },
    )
