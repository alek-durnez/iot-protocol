import matplotlib.pyplot as plt
import csv
import sys

LOG_FILE = "results/experiment_log.csv"


def plot_experiment():
    timestamps = []
    battery_levels = []
    tx_events = []
    modes = []

    try:
        with open(LOG_FILE, 'r') as f:
            reader = csv.DictReader(f)
            start_time = None
            packet_count = 0

            for row in reader:
                t = float(row["Timestamp"])
                if start_time is None: start_time = t

                timestamps.append(t - start_time)  # Relative time (0s start)
                battery_levels.append(float(row["Battery"]))
                modes.append(row["Mode"])

                packet_count += 1
                tx_events.append(packet_count)

    except FileNotFoundError:
        print("Error: Run 'main.py' first to generate data!")
        sys.exit()

    # --- THE VISUALIZATION ---
    fig, ax1 = plt.subplots(figsize=(10, 6))

    # Plot 1: Battery Drain (Left Y-Axis)
    color = 'tab:red'
    ax1.set_xlabel('Time (seconds)')
    ax1.set_ylabel('Battery Level (%)', color=color)
    ax1.plot(timestamps, battery_levels, color=color, linewidth=2, label='Battery Life')
    ax1.tick_params(axis='y', labelcolor=color)
    ax1.grid(True, linestyle='--', alpha=0.6)

    # Plot 2: Transmission Events (Right Y-Axis)
    ax2 = ax1.twinx()
    color = 'tab:blue'
    ax2.set_ylabel('Cumulative Transmissions (TX Events)', color=color)
    ax2.step(timestamps, tx_events, where='post', color=color, linewidth=2, label='Packets Sent')
    ax2.tick_params(axis='y', labelcolor=color)

    # Add Mode Annotations
    plt.title('Impact of Adaptive Aggregation on Radio Activity')

    # Show the graph
    plt.tight_layout()
    print("Generating plot...")
    plt.show()


if __name__ == "__main__":
    plot_experiment()