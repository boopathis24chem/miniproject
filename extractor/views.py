from django.shortcuts import render
from django.http import HttpResponse
from .models import Experiment

import matplotlib.pyplot as plt
import numpy as np
import io


# -----------------------------
# MAIN CALCULATION VIEW
# -----------------------------
def calculate(request):

    if request.method == "POST":
        # Input
        flow = float(request.POST['flow_rate'])
        rpm = int(request.POST['rpm'])
        water = float(request.POST['water'])
        acetone = float(request.POST['acetone'])

        # -----------------------------
        # Concentration Check
        # -----------------------------
        total = water + acetone
        if abs(total - 100) > 0.5:
            return render(request, 'result.html', {
                're': 0,
                'eff': 0,
                'msg': f"❌ Water + Acetone must be 100% (Now = {total}%)"
            })

        # -----------------------------
        # Reynolds Number
        # -----------------------------
        reynolds = flow * rpm * 0.1

        # -----------------------------
        # Efficiency Model
        # -----------------------------
        base_eff = water / (water + acetone)

        rpm_effect = (rpm / 2000) * (1 - (rpm / 3000))
        flow_effect = 1 / (1 + 0.1 * flow)

        efficiency = base_eff * rpm_effect * flow_effect * 100
        efficiency = round(efficiency, 2)

        # Limit
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

        if len(suggestions) == 0:
            suggestions.append("Operating in acceptable range")

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

        # -----------------------------
        # RETURN
        # -----------------------------
        return render(request, 'result.html', {
            're': reynolds,
            'eff': efficiency,
            'msg': msg
        })

    return render(request, 'form.html')


# -----------------------------
# GRAPH VIEW (FINAL)
# -----------------------------
from django.http import HttpResponse
import matplotlib.pyplot as plt
import io
from .models import Experiment

def multi_graph(request):
    data = Experiment.objects.all()

    rpm = [d.rpm for d in data]
    flow = [d.flow_rate for d in data]
    efficiency = [d.efficiency for d in data]
    water = [d.water_conc for d in data]

    if len(rpm) == 0:
        return HttpResponse("No data available")

    plt.figure(figsize=(8,6))

    # -----------------------------
    # GRAPH 1: RPM vs Efficiency
    # -----------------------------
    plt.plot(rpm, efficiency, marker='o', label="RPM vs Efficiency")

    # -----------------------------
    # GRAPH 2: Flow vs Efficiency
    # -----------------------------
    plt.plot(flow, efficiency, marker='x', label="Flow vs Efficiency")

    # -----------------------------
    # GRAPH 3: Concentration vs Efficiency
    # -----------------------------
    plt.plot(water, efficiency, marker='s', label="Conc vs Efficiency")

    # Labels
    plt.xlabel("Input Parameters")
    plt.ylabel("Efficiency (%)")
    plt.title("Multi-Parameter Efficiency Analysis")

    plt.legend()
    plt.grid()

    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    plt.close()
    buffer.seek(0)

    return HttpResponse(buffer.getvalue(), content_type='image/png')