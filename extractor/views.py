import matplotlib
matplotlib.use('Agg')   # IMPORTANT for server

import matplotlib.pyplot as plt
import io

from django.shortcuts import render
from django.http import HttpResponse
from .models import Experiment


# -----------------------------
# MAIN CALCULATION
# -----------------------------
def calculate(request):

    if request.method == "POST":
        flow = float(request.POST["flow_rate"])
        rpm = int(request.POST["rpm"])
        water = float(request.POST["water"])
        acetone = float(request.POST["acetone"])

        # -----------------------------
        # VALIDATION
        # -----------------------------
        total = water + acetone
        if abs(total - 100) > 0.5:
            return render(request, "result.html", {
                "flow": flow,
                "rpm": rpm,
                "water": water,
                "acetone": acetone,
                "re": 0,
                "eff": 0,
                "msg": f"❌ Water + Acetone must be 100% (Now = {total}%)"
            })

        # -----------------------------
        # CALCULATION
        # -----------------------------
        reynolds = flow * rpm * 0.1

        base_eff = water / (water + acetone)
        rpm_effect = (rpm / 2000) * (1 - (rpm / 3000))
        flow_effect = 1 / (1 + 0.1 * flow)

        efficiency = base_eff * rpm_effect * flow_effect * 100
        efficiency = round(efficiency, 2)
        efficiency = max(0, min(100, efficiency))

        # -----------------------------
        # MESSAGE
        # -----------------------------
        if efficiency < 30:
            msg = "⚠ Very Low efficiency"
        elif efficiency < 60:
            msg = "⚠ Moderate efficiency"
        elif efficiency < 85:
            msg = "✅ Good efficiency"
        else:
            msg = "🔥 Excellent efficiency"

        # -----------------------------
        # SUGGESTIONS
        # -----------------------------
        suggestions = []

        if rpm < 1500:
            suggestions.append("Increase RPM")
        elif rpm > 2600:
            suggestions.append("Reduce RPM")

        if flow > 8:
            suggestions.append("Reduce Flow Rate")
        elif flow < 2:
            suggestions.append("Increase Flow Rate")

        if water < 60:
            suggestions.append("Increase Water concentration")

        if not suggestions:
            suggestions.append("Need improvement for the Better Efficiency...")

        msg = msg + " | " + ", ".join(suggestions)

        # -----------------------------
        # SAVE DATA
        # -----------------------------
        Experiment.objects.create(
            flow_rate=flow,
            rpm=rpm,
            water_conc=water,
            acetone_conc=acetone,
            reynolds=reynolds,
            efficiency=efficiency
        )

        return render(request, "result.html", {
            "flow": flow,
            "rpm": rpm,
            "water": water,
            "acetone": acetone,
            "re": reynolds,
            "eff": efficiency,
            "msg": msg
        })

    return render(request, "form.html")


# -----------------------------
# GRAPH TEMPLATE FUNCTION
# -----------------------------
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


# -----------------------------
# RPM GRAPH
# -----------------------------
def rpm_graph(request):
    data = Experiment.objects.all()
    x = [d.rpm for d in data]
    y = [d.efficiency for d in data]

    if not x:
        return HttpResponse("No data available")

    buffer = generate_graph(x, y, "RPM", "RPM vs Efficiency")
    return HttpResponse(buffer.getvalue(), content_type='image/png')


# -----------------------------
# FLOW GRAPH
# -----------------------------
def flow_graph(request):
    data = Experiment.objects.all()
    x = [d.flow_rate for d in data]
    y = [d.efficiency for d in data]

    if not x:
        return HttpResponse("No data available")

    buffer = generate_graph(x, y, "Flow Rate (L/min)", "Flow vs Efficiency")
    return HttpResponse(buffer.getvalue(), content_type='image/png')


# -----------------------------
# WATER GRAPH
# -----------------------------
def water_graph(request):
    data = Experiment.objects.all()
    x = [d.water_conc for d in data]
    y = [d.efficiency for d in data]

    if not x:
        return HttpResponse("No data available")

    buffer = generate_graph(x, y, "Water Concentration (%)", "Water vs Efficiency")
    return HttpResponse(buffer.getvalue(), content_type='image/png')


# -----------------------------
# ACETONE GRAPH
# -----------------------------
def acetone_graph(request):
    data = Experiment.objects.all()
    x = [d.acetone_conc for d in data]
    y = [d.efficiency for d in data]

    if not x:
        return HttpResponse("No data available")

    buffer = generate_graph(x, y, "Acetone Concentration (%)", "Acetone vs Efficiency")
    return HttpResponse(buffer.getvalue(), content_type='image/png')