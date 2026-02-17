import matplotlib.pyplot as plt
import os

# Ensure results directory exists
os.makedirs("results", exist_ok=True)

# --- CONFIGURATION ---
# Enter the results from your main.py console output here
# (Example values based on your recent 50-reading test)
labels = ['Standard CoAP', 'Smart Protocol']

# Metric 1: Packets Sent (Lower is better)
packets = [50, 8]

# Metric 2: Bytes Transferred (Lower is better)
bytes_transferred = [1450, 401]

# Metric 3: Energy Consumed (Lower is better)
energy = [895.0, 160.1]


# --- PLOTTING ---
def create_comparison_chart():
    print("Generating Head-to-Head Comparison Graph...")

    fig, axes = plt.subplots(1, 3, figsize=(16, 6))

    # Colors: Red = Standard/Expensive, Green = Smart/Efficient
    colors = ['#e74c3c', '#2ecc71']

    # Plot 1: Packet Count
    axes[0].bar(labels, packets, color=colors, alpha=0.8)
    axes[0].set_title('Total Packets Sent\n(Radio Wake-ups)', fontsize=12, fontweight='bold')
    axes[0].set_ylabel('Count')
    axes[0].grid(axis='y', linestyle='--', alpha=0.5)
    for i, v in enumerate(packets):
        axes[0].text(i, v + 1, str(v), ha='center', fontweight='bold', fontsize=11)

    # Plot 2: Bandwidth
    axes[1].bar(labels, bytes_transferred, color=colors, alpha=0.8)
    axes[1].set_title('Total Network Traffic\n(Bandwidth Usage)', fontsize=12, fontweight='bold')
    axes[1].set_ylabel('Bytes')
    axes[1].grid(axis='y', linestyle='--', alpha=0.5)
    for i, v in enumerate(bytes_transferred):
        axes[1].text(i, v + 50, f"{v} B", ha='center', fontweight='bold', fontsize=11)

    # Plot 3: Energy Efficiency
    axes[2].bar(labels, energy, color=colors, alpha=0.8)
    axes[2].set_title('Total Energy Consumed\n(Battery Impact)', fontsize=12, fontweight='bold')
    axes[2].set_ylabel('Energy (mJ)')
    axes[2].grid(axis='y', linestyle='--', alpha=0.5)
    for i, v in enumerate(energy):
        axes[2].text(i, v + 20, f"{v:.1f} mJ", ha='center', fontweight='bold', fontsize=11)

    # Global Title
    plt.suptitle('Benchmark Results: Standard CoAP vs. Smart Protocol\n(Scenario: 50 Sensor Readings, 20% Packet Loss)',
                 fontsize=16)

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])  # Make room for suptitle

    output_path = "results/comparison_graph.png"
    plt.savefig(output_path, dpi=300)
    print(f"Graph saved successfully to: {output_path}")
    plt.show()


if __name__ == "__main__":
    create_comparison_chart()