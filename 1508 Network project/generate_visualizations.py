import matplotlib.pyplot as plt
import numpy as np

methods = ['Method 1\nSemantic', 'Method 2\nPerformance', 'Method 3\nLLM']
accuracy = [69.0, 72.8, 94.7]
accuracy_std = [0.0, 1.5, 0.6]
in_domain = [91.8, 94.2, 99.2]
in_domain_std = [0.5, 0.8, 0.2]

colors = ['#FF6B6B', '#FFD93D', '#6BCB77']

# ============================================
# Visualization 1: Accuracy & In-Domain Rates
# ============================================
fig, ax = plt.subplots(figsize=(12, 7))

x = np.arange(len(methods))
width = 0.35

bars1 = ax.bar(x - width/2, accuracy, width, label='Routing Accuracy', 
               color=colors, alpha=0.8, edgecolor='black', linewidth=1.5)
bars2 = ax.bar(x + width/2, in_domain, width, label='In-Domain Rate',
               color=colors, alpha=0.5, edgecolor='black', linewidth=1.5, hatch='//')

# Add error bars
ax.errorbar(x - width/2, accuracy, yerr=accuracy_std, fmt='none', color='black', 
           capsize=5, capthick=2, linewidth=2)
ax.errorbar(x + width/2, in_domain, yerr=in_domain_std, fmt='none', color='black',
           capsize=5, capthick=2, linewidth=2)

# Customize
ax.set_xlabel('Routing Method', fontsize=12, weight='bold')
ax.set_ylabel('Rate (%)', fontsize=12, weight='bold')
ax.set_title('Routing Accuracy vs In-Domain Rate\nFive-Trial Evaluation (Mean ± Std Dev)', 
             fontsize=14, weight='bold', pad=20)
ax.set_xticks(x)
ax.set_xticklabels(methods, fontsize=11)
ax.set_ylim(60, 105)
ax.legend(fontsize=11, loc='lower right')
ax.grid(axis='y', alpha=0.3, linestyle='--')

# Add value labels on bars
for bars in [bars1, bars2]:
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.1f}%', ha='center', va='bottom', fontsize=10, weight='bold')

plt.tight_layout()
plt.savefig('accuracy_visualization.png', dpi=300, bbox_inches='tight', facecolor='white')
print("✓ Saved: accuracy_visualization.png")
plt.close()

# ============================================
# Visualization 2: Latency & Quality Trade-off
# ============================================
fig, ax1 = plt.subplots(figsize=(12, 7))

# Primary axis: Latency
latency = [5.49, 6.80, 8.24]
routing_overhead = [11.5, 12.0, 2410.6]
quality = [4.41, 4.50, 4.53]

x = np.arange(len(methods))
width = 0.25

bars1 = ax1.bar(x - width, latency, width, label='Total Latency (s)', 
                color='#4A90E2', alpha=0.8, edgecolor='black', linewidth=1.5)

ax1.set_xlabel('Routing Method', fontsize=12, weight='bold')
ax1.set_ylabel('Latency (seconds)', fontsize=12, weight='bold', color='#4A90E2')
ax1.set_xticks(x)
ax1.set_xticklabels(methods, fontsize=11)
ax1.tick_params(axis='y', labelcolor='#4A90E2')
ax1.grid(axis='y', alpha=0.3, linestyle='--')

# Secondary axis: Quality
ax2 = ax1.twinx()
bars2 = ax2.bar(x, quality, width, label='Answer Quality (5pts)', 
                color='#50C878', alpha=0.8, edgecolor='black', linewidth=1.5)

ax2.set_ylabel('Quality Score (5-point scale)', fontsize=12, weight='bold', color='#50C878')
ax2.set_ylim(4.0, 4.7)
ax2.tick_params(axis='y', labelcolor='#50C878')

# Routing overhead as text annotation
for i, (method, overhead) in enumerate(zip(methods, routing_overhead)):
    if overhead > 100:
        ax1.text(i - width, latency[i] + 0.3, f'Route: {overhead:.0f}ms', 
                ha='center', fontsize=9, style='italic', color='#666')

# Add value labels
for bars in [bars1, bars2]:
    for bar in bars:
        height = bar.get_height()
        label = f'{height:.2f}' if height < 10 else f'{height:.1f}'
        ax1.text(bar.get_x() + bar.get_width()/2., height + 0.15 if bars == bars1 else height + 0.02,
                label, ha='center', va='bottom', fontsize=10, weight='bold')

# Title and legend
plt.title('Latency vs Quality Trade-off\nEnd-to-End Performance Analysis', 
         fontsize=14, weight='bold', pad=20)

lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, fontsize=11, loc='upper left')

fig.tight_layout()
plt.savefig('latency_quality_visualization.png', dpi=300, bbox_inches='tight', facecolor='white')
print("✓ Saved: latency_quality_visualization.png")
plt.close()

# ============================================
# Visualization 3: Efficiency Frontier
# ============================================
fig, ax = plt.subplots(figsize=(12, 7))

# Plot accuracy vs total latency
methods_short = ['Semantic', 'Performance', 'LLM Meta']
ax.scatter(latency, accuracy, s=500, c=colors, alpha=0.7, edgecolors='black', linewidth=2)

# Add method labels
for i, method in enumerate(methods_short):
    ax.annotate(method, (latency[i], accuracy[i]), 
               xytext=(10, 10), textcoords='offset points',
               fontsize=11, weight='bold',
               bbox=dict(boxstyle='round,pad=0.5', facecolor=colors[i], alpha=0.3),
               arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0'))

# Add efficiency contours
for efficiency in [0.10, 0.15, 0.20, 0.25]:
    acc_range = np.linspace(60, 100, 100)
    lat_range = (max(accuracy) - acc_range) / efficiency + 5
    ax.plot(lat_range, acc_range, '--', alpha=0.2, color='gray', linewidth=1)

ax.set_xlabel('Total Latency (seconds)', fontsize=12, weight='bold')
ax.set_ylabel('Routing Accuracy (%)', fontsize=12, weight='bold')
ax.set_title('Accuracy-Latency Trade-off Frontier\nOptimal Method Selection by Use Case', 
            fontsize=14, weight='bold', pad=20)
ax.grid(alpha=0.3, linestyle='--')
ax.set_xlim(5, 9)
ax.set_ylim(65, 100)

# Add use case annotations
ax.text(5.49, 65, 'Low-Latency\nApplications', fontsize=10, 
       bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.7))
ax.text(6.80, 75, 'Balanced\nRequirements', fontsize=10,
       bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.7))
ax.text(8.24, 92, 'Quality-\nCritical', fontsize=10,
       bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.7))

plt.tight_layout()
plt.savefig('efficiency_frontier.png', dpi=300, bbox_inches='tight', facecolor='white')
print("✓ Saved: efficiency_frontier.png")
plt.close()

print("\nAll three visualizations generated successfully!")
print("\nGenerated files:")
print("  1. accuracy_visualization.png - Accuracy & In-Domain Rate comparison")
print("  2. latency_quality_visualization.png - Latency vs Quality trade-off")
print("  3. efficiency_frontier.png - Accuracy-Latency efficiency frontier")
