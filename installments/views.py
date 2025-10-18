from django.shortcuts import render
from plots.models import Plot
from django.contrib.auth.decorators import login_required


@login_required
def home(request):
    total_plots = Plot.objects.count()
    available = Plot.objects.filter(status="available").count()
    reserved = Plot.objects.filter(status="reserved").count()
    sold = Plot.objects.filter(status="sold").count()

    featured_plots = Plot.objects.filter(status="available")[:6]  # show 6 available

    context = {
        "total_plots": total_plots,
        "available": available,
        "reserved": reserved,
        "sold": sold,
        "featured_plots": featured_plots,
    }
    return render(request, "home.html", context)


def contact(request):
    return render(request, "contact.html")
