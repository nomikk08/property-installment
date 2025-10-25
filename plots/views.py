from django.shortcuts import render
from django.db.models import Sum
from .models import Plot
from django.contrib.auth.decorators import login_required


@login_required
def plot_list(request):
    plots = Plot.objects.all()

    # Filters
    status = request.GET.get("status")
    plot_type = request.GET.get("plot_type")
    min_size = request.GET.get("min_size")
    max_size = request.GET.get("max_size")
    min_price = request.GET.get("min_price")
    max_price = request.GET.get("max_price")
    is_corner = request.GET.get("is_corner")

    if status:
        plots = plots.filter(status=status)

    if plot_type:
        plots = plots.filter(plot_type=plot_type)

    if min_size:
        plots = plots.filter(size_sqft__gte=min_size)
    if max_size:
        plots = plots.filter(size_sqft__lte=max_size)

    if min_price:
        plots = plots.filter(price__gte=min_price)
    if max_price:
        plots = plots.filter(price__lte=max_price)

    if is_corner == "true":
        plots = plots.filter(is_corner=True)

    # ✅ Sqft stats
    total_sqft = Plot.objects.aggregate(total=Sum("size_sqft"))["total"] or 0
    available_sqft = Plot.objects.filter(status="available").aggregate(total=Sum("size_sqft"))["total"] or 0
    sold_sqft = Plot.objects.filter(status="sold").aggregate(total=Sum("size_sqft"))["total"] or 0

    context = {
        "plots": plots,
        "selected_status": status,
        "selected_plot_type": plot_type,
        "min_size": min_size,
        "max_size": max_size,
        "min_price": min_price,
        "max_price": max_price,
        "is_corner": is_corner,
        "total_sqft": total_sqft,
        "available_sqft": available_sqft,
        "sold_sqft": sold_sqft,
    }
    return render(request, "plots/plot_list.html", context)
