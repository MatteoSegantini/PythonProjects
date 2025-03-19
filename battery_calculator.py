import matplotlib.pyplot as plt
import streamlit as st
import numpy as np

st.set_page_config(layout="wide")

# Title
st.title("Energy Consumption Calculator")

# Description
st.write("Adjust the parameters below to see how they impact energy budget and related battery volume.")

col1, col2, col3 = st.columns([5,1,6])

with col1:
    # Define variable parameters
    shelf_life              = st.slider("Shelf-Life  [years]", min_value=1, max_value=10, value=5, step=1)
    wakeup_interval         = st.slider("Wake-Up Interval [s]", min_value=1, max_value=30, value=10)
    lifetime                = st.slider("Sensor Lifetime [months]", min_value=1, max_value=12, value=12, step=1)
    activity_monitoring_f   = st.slider("Activity Monitoring Frequency [Hz]", min_value=0.0, max_value=2.0, value=1.0, step=0.5)
    meas_f                  = st.slider("Measurement Frequency [Hz]", min_value=5, max_value=20, value=10, step=1)
    transmission_rate       = st.slider("Transmission Interval [days]", min_value=1, max_value=3, value=1, step=1)

# Define fixed parameters
self_discharge  = 1     # %
power_switch    = 10    # nA
wakeup_timer    = 20    # nA
meas_14bit      = 25    # uA
on_time_14bit   = 2     # ms
meas_18bit      = 60    # uA
on_time_18bit   = 7.76  # ms
memory          = 50    # nA
data_buffer     = 10    # nA
data_processing = 500   # uA
on_time_process = 50    # ms
data_process_f  = 50    # s
connection_time = 2     # s
connection_curr = 10    # mA

# Assumption for Self-Discharge
batt_capacity   = 15    # mAh
activity_rate   = 10    # %

# Calculation Section
shelf_life_consumption = {
    "Self-Discharge"        : batt_capacity * (self_discharge/100) * shelf_life,
    "Power Switch"          : power_switch * 8760 * shelf_life / 1e6,
    "Wakeup Timer"          : wakeup_timer * 8760 * shelf_life / 1e6,
    "Wakeup Measurement"    : ((meas_14bit/1e3) * (on_time_14bit/1e3) / wakeup_interval) * 8760 * shelf_life
}

operation_consumption = {
    "Self-Discharge"        : batt_capacity * (self_discharge/100) * (lifetime/12),
    "Power Switch"          : power_switch * (24*365 * lifetime/12) / 1e6,
    "Wakeup Timer"          : wakeup_timer * (24*365 * lifetime/12) / 1e6,
    "Activity Measurement"  : (meas_14bit/1e3) * (on_time_14bit/1e3) * activity_monitoring_f * (24*365 * lifetime/12),
    "Measurement"           : (meas_18bit/1e3) * (on_time_18bit/1e3) * meas_f * (24*365 * lifetime/12) * (activity_rate/100),
    "Memory"                : (memory/1e6) * (24*365 * lifetime/12) * (activity_rate/100),
    "Data Buffer"           : (data_buffer/1e6) * (24*365 * lifetime/12),
    "Data Processing"       : ((data_processing/1e3) * (on_time_process/1e3) / data_process_f) * (24*365 * lifetime/12) * (activity_rate/100)
}

transmission_consumption = {
    "Transmission"          : (connection_curr * connection_time / 3600) * (365 * lifetime/12) / transmission_rate
}

power_consumption = (
    sum(shelf_life_consumption.values()) +
    sum(operation_consumption.values()) +
    sum(transmission_consumption.values())
)

# Volume Conversion
a = 5.60373414
b = -0.00963755
c = -6.00269058
vol_temp = -np.log((power_consumption-c)/a)/b
safety_margin = 0
vol = vol_temp + vol_temp*safety_margin/100

# Data for the plot
categories = ["Shelf-Life", "Operation", "Data Transmission"]
values = [
    sum(shelf_life_consumption.values()),
    sum(operation_consumption.values()),
    sum(transmission_consumption.values())
]

# Set plot style based on your config
fig_bg = "#2E2E2E"
ax_bg = "#2E2E2E"
text_color = "#FFFFFF"
grid_color = "gray"
colors = ["#4c9be8", "#ffae49", "#63c05b"]
edge_color = "#FFFFFF"

with col3:
    st.markdown(
        """
        <div style='width: 600px; text-align: left;'>
            <h1 style='font-size: 32px;'>Estimated Battery Capacity<sup>*</sup>: {:.2f} mAh</h1>
        </div>
        """.format(power_consumption),
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div style='width: 600px; text-align: left;'>
            <h1 style='font-size: 32px;'>Estimated Battery Volume<sup>*</sup>: {:.0f} mm<sup>3</sup><br></h1>
        </div>
        """.format(vol),
        unsafe_allow_html=True
    )

    st.markdown("<p><sup>*</sup> Based on current design and assumption. Subject to change.</p>",
                unsafe_allow_html=True)

    fig, ax = plt.subplots(figsize=(8, 5), facecolor=fig_bg)
    ax.set_facecolor(ax_bg)

    # Plot the bar chart
    bars = ax.bar(categories, values, color=colors, edgecolor=edge_color, linewidth=1.2)

    # Add values on top of bars
    for bar in bars:
        height = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            height - 0.5,
            f"{height:.2f} mAh",
            ha='center',
            fontsize=12,
            fontweight='bold',
            color=text_color
        )

    # Style the chart
    ax.set_xlabel("Mode", fontsize=14, fontweight='bold', color=text_color, labelpad=10)
    ax.set_ylabel("Energy Consumption (mAh)", fontsize=14, fontweight='bold', color=text_color, labelpad=10)
    ax.set_title("Energy Consumption Breakdown", fontsize=16, fontweight='bold', color=text_color, pad=15)
    ax.yaxis.grid(True, linestyle="--", alpha=0.4, color=grid_color)
    ax.set_axisbelow(True)
    ax.tick_params(axis='x', colors=text_color)
    ax.tick_params(axis='y', colors=text_color)

    # Remove top and right borders
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color(text_color)
    ax.spines["bottom"].set_color(text_color)

    st.pyplot(fig)
