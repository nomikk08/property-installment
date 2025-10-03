from django.shortcuts import render
from .models import Plot, InstallmentPlan

def plot_list(request):
    plots = Plot.objects.all().select_related()
    plans = InstallmentPlan.objects.all()

    plan_id = request.GET.get("plan")
    status = request.GET.get("status")

    if plan_id:
        plots = plots.filter(booking__plan_id=plan_id)
    if status:
        plots = plots.filter(status=status)

    context = {
        "plots": plots,
        "plans": plans,
        "selected_plan": plan_id,
        "selected_status": status,
    }
    return render(request, "plots/plot_list.html", context)
