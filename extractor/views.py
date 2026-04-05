import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt
import io

from django.shortcuts import render
from django.http import HttpResponse
from .models import Experiment


def calculate(request):
    if request.method == "POST":
        flow = float(request.POST["flow_rate"])
        rpm = int(request.POST["rpm"])

        initial_water = float(request.POST["initial_water"])
        initial_oil = float(request.POST["initial_oil"])

        final_water = float(request.POST["final_water"])
        final_oil = float(request.POST["final_oil"])

        if abs((initial_water + initial_oil) - 100) > 0.5:
            return render(request, "result.html", {
                "flow": flow,
                "rpm": rpm,
                "initial_water": initial_water,
                "initial_oil": initial_oil,
                "final_water": final_water,
                "final_oil": final_oil,
                "eff": 0,
                "msg": "❌ Initial water + oil must be 100%"
            })

        if abs((final_water + final_oil) - 100) > 0.5:
            return render(request, "result.html", {
                "flow": flow,
                "rpm": rpm,
                "initial_water": initial_water,
                "initial_oil": initial_oil,
                "final_water": final_water,
                "final_oil": final_oil,
                "eff": 0,
                "msg": "❌ Final water + oil must be 100%"
            })

        if final_water <= initial_water:
            efficiency = 0
        else:
            base_eff = ((final_water - initial_water) / (100 - initial_water)) * 100
            rpm_factor = rpm / 2000
            flow_factor = 1 / (1 + 0.1 * flow)
            efficiency = base_eff * rpm_factor * flow_factor

        efficiency = round(efficiency, 2)
        efficiency = max(0, min(100, efficiency))

        if efficiency < 30:
            msg = "⚠ Very Low efficiency"
        elif efficiency < 60:
            msg = "⚠ Moderate efficiency"
        elif efficiency < 85:
            msg = "✅ Good efficiency"
        else:
            msg = "🔥 Excellent efficiency"

        suggestions = []

        if rpm < 1500:
            suggestions.append("Increase RPM")
        elif rpm > 2600:
            suggestions.append("Reduce RPM")

        if flow > 8:
            suggestions.append("Reduce Flow Rate")

        if final_water < 80:
            suggestions.append("Improve separation")

        if not suggestions:
            suggestions.append("Operating in optimal range")

        msg = msg + " | " + ", ".join(suggestions)

        Experiment.objects.create(
            flow_rate=flow,
            rpm=rpm,
            initial_water_conc=initial_water,
            initial_oil_conc=initial_oil,
            final_water_conc=final_water,
            final_oil_conc=final_oil,
            efficiency=efficiency
        )

        return render(request, "result.html", {
            "flow": flow,
            "rpm": rpm,
            "initial_water": initial_water,
            "initial_oil": initial_oil,
            "final_water": final_water,
            "final_oil": final_oil,
            "eff": efficiency,
            "msg": msg
        })

    return render(request, "form.html")


def generate_graph(x, y, xlabel, title):
    fig, ax = plt.subplots()
    ax.scatter(x, y)
    ax.set_xlabel(xlabel)
    ax.set_ylabel("Efficiency (%)")
    ax.set_title(title)
    ax.grid(True)

    buffer = io.BytesIO()
    fig.savefig(buffer, format='png')
    plt.close(fig)
    buffer.seek(0)
    return buffer


def rpm_graph(request):
    data = Experiment.objects.all()
    x = [d.rpm for d in data]
    y = [d.efficiency for d in data]

    if not x:
        return HttpResponse("No data")

    buffer = generate_graph(x, y, "RPM", "RPM vs Efficiency")
    return HttpResponse(buffer.getvalue(), content_type='image/png')


def flow_graph(request):
    data = Experiment.objects.all()
    x = [d.flow_rate for d in data]
    y = [d.efficiency for d in data]

    if not x:
        return HttpResponse("No data")

    buffer = generate_graph(x, y, "Flow Rate (L/min)", "Flow vs Efficiency")
    return HttpResponse(buffer.getvalue(), content_type='image/png')