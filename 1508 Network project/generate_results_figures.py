"""Generate publication-quality figures for the Results section."""

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from matplotlib.gridspec import GridSpec

# Set style for publication quality
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

# Data from 5 trials
seeds = [22, 32, 52, 62, 82]

# Method 1: Semantic (constant across seeds)
semantic_accuracy = [69.0, 69.0, 69.0, 69.0, 69.0]
semantic_indomain = [91.5, 91.5, 92.5, 92.5, 93.0]
semantic_latency = [5.15, 5.42, 5.50, 5.32, 5.79]

# Method 2: Performance-weighted
performance_accuracy = [72.5, 73.0, 75.0, 71.0, 74.0]
performance_indomain = [93.5, 95.0, 95.5, 93.5, 94.5]
performance_latency = [8.16, 5.18, 5.24, 7.69, 5.56]

# Method 3: LLM
llm_accuracy = [95.5, 95.5, 95.5, 94.5, 94.0]
llm_indomain = [99.0, 99.0, 99.0, 99.0, 99.5]
llm_latency = [9.10, 7.81, 7.81, 7.97, 7.73]

# Quality metrics (from spot check)
quality_scores = {
    'Semantic': 4.41,
    'Performance': 4.50,
    'LLM': 4.53
}

# Create figure with multiple subplots
fig = plt.figure(figsize=(16, 12))
gs = GridSpec(3, 3, figure=fig, hspace=0.35, wspace=0.3)

# ========================
# Row 1: Accuracy Analysis
# ========================

# 1.1: Accuracy across trials
ax1 = fig.add_subplot(gs[0, 0])
x = np.arange(len(seeds))
width = 0.25

ax1.bar(x - width, semantic_accuracy, width, label='Semantic', alpha=0.8)
ax1.bar(x, performance_accuracy, width, label='Performance', alpha=0.8)
ax1.bar(x + width, llm_accuracy, width, label='LLM', alpha=0.8)

ax1.set_xlabel('Seed', fontsize=11, fontweight='bold')
ax1.set_ylabel('Accuracy (%)', fontsize=11, fontweight='bold')
ax1.set_title('Routing Accuracy Across 5 Trials', fontsize=12, fontweight='bold')
ax1.set_xticks(x)
ax1.set_xticklabels(seeds)
ax1.set_ylim([65, 100])
ax1.legend(fontsize=10)
ax1.grid(True, alpha=0.3)

# 1.2: Accuracy means with error bars
ax2 = fig.add_subplot(gs[0, 1])
methods = ['Semantic', 'Performance', 'LLM']
means = [69.0, 72.8, 94.7]
stds = [0.0, 1.5, 0.6]
colors = ['#1f77b4', '#ff7f0e', '#2ca02c']

bars = ax2.bar(methods, means, yerr=stds, capsize=10, color=colors, alpha=0.7, edgecolor='black', linewidth=2)
ax2.set_ylabel('Accuracy (%)', fontsize=11, fontweight='bold')
ax2.set_title('Mean Accuracy with Std Dev', fontsize=12, fontweight='bold')
ax2.set_ylim([65, 100])
ax2.grid(True, alpha=0.3, axis='y')

# Add value labels on bars
for bar, mean, std in zip(bars, means, stds):
    height = bar.get_height()
    ax2.text(bar.get_x() + bar.get_width()/2., height + std + 1,
            f'{mean:.1f}%', ha='center', va='bottom', fontsize=10, fontweight='bold')

# 1.3: Accuracy improvement vs baseline
ax3 = fig.add_subplot(gs[0, 2])
improvements = [0, 72.8-69.0, 94.7-69.0]
method_labels = ['Baseline', 'Performance\n(+3.8pp)', 'LLM\n(+25.7pp)']
colors_imp = ['gray', '#ff7f0e', '#2ca02c']

bars = ax3.bar(method_labels, improvements, color=colors_imp, alpha=0.7, edgecolor='black', linewidth=2)
ax3.set_ylabel('Accuracy Gain vs Baseline (%pp)', fontsize=11, fontweight='bold')
ax3.set_title('Accuracy Improvement Over Semantic', fontsize=12, fontweight='bold')
ax3.grid(True, alpha=0.3, axis='y')

for bar, imp in zip(bars, improvements):
    height = bar.get_height()
    if height > 0:
        ax3.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                f'{imp:.1f}pp', ha='center', va='bottom', fontsize=10, fontweight='bold')

# ========================
# Row 2: In-Domain & Latency
# ========================

# 2.1: In-Domain rates across trials
ax4 = fig.add_subplot(gs[1, 0])
ax4.plot(seeds, semantic_indomain, marker='o', linewidth=2.5, markersize=8, label='Semantic', alpha=0.8)
ax4.plot(seeds, performance_indomain, marker='s', linewidth=2.5, markersize=8, label='Performance', alpha=0.8)
ax4.plot(seeds, llm_indomain, marker='^', linewidth=2.5, markersize=8, label='LLM', alpha=0.8)

ax4.set_xlabel('Seed', fontsize=11, fontweight='bold')
ax4.set_ylabel('In-Domain Rate (%)', fontsize=11, fontweight='bold')
ax4.set_title('Agent Self-Assessment Across Trials', fontsize=12, fontweight='bold')
ax4.set_ylim([88, 100])
ax4.legend(fontsize=10)
ax4.grid(True, alpha=0.3)

# 2.2: Latency comparison (per-query)
ax5 = fig.add_subplot(gs[1, 1])
latency_means = [5.49, 6.80, 8.24]
latency_stds = [0.23, 1.22, 0.59]

bars = ax5.bar(methods, latency_means, yerr=latency_stds, capsize=10, color=colors, alpha=0.7, edgecolor='black', linewidth=2)
ax5.set_ylabel('Latency (seconds)', fontsize=11, fontweight='bold')
ax5.set_title('Mean End-to-End Latency', fontsize=12, fontweight='bold')
ax5.grid(True, alpha=0.3, axis='y')

for bar, mean, std in zip(bars, latency_means, latency_stds):
    height = bar.get_height()
    ax5.text(bar.get_x() + bar.get_width()/2., height + std + 0.1,
            f'{mean:.2f}s', ha='center', va='bottom', fontsize=10, fontweight='bold')

# 2.3: Accuracy vs Latency tradeoff
ax6 = fig.add_subplot(gs[1, 2])
# Plot individual trials
for i, (seed, sem_acc, perf_acc, llm_acc, sem_lat, perf_lat, llm_lat) in enumerate(
    zip(seeds, semantic_accuracy, performance_accuracy, llm_accuracy, 
        semantic_latency, performance_latency, llm_latency)):
    if i == 0:  # Only add labels for first point
        ax6.scatter(sem_lat, sem_acc, s=120, alpha=0.6, label='Semantic', color='#1f77b4', edgecolors='black', linewidth=1.5)
        ax6.scatter(perf_lat, perf_acc, s=120, alpha=0.6, label='Performance', color='#ff7f0e', edgecolors='black', linewidth=1.5)
        ax6.scatter(llm_lat, llm_acc, s=120, alpha=0.6, label='LLM', color='#2ca02c', edgecolors='black', linewidth=1.5)
    else:
        ax6.scatter(sem_lat, sem_acc, s=120, alpha=0.6, color='#1f77b4', edgecolors='black', linewidth=1.5)
        ax6.scatter(perf_lat, perf_acc, s=120, alpha=0.6, color='#ff7f0e', edgecolors='black', linewidth=1.5)
        ax6.scatter(llm_lat, llm_acc, s=120, alpha=0.6, color='#2ca02c', edgecolors='black', linewidth=1.5)

# Add mean points with larger markers
ax6.scatter(np.mean(semantic_latency), np.mean(semantic_accuracy), s=300, marker='D', 
           color='#1f77b4', edgecolors='black', linewidth=2, zorder=5)
ax6.scatter(np.mean(performance_latency), np.mean(performance_accuracy), s=300, marker='D', 
           color='#ff7f0e', edgecolors='black', linewidth=2, zorder=5)
ax6.scatter(np.mean(llm_latency), np.mean(llm_accuracy), s=300, marker='D', 
           color='#2ca02c', edgecolors='black', linewidth=2, zorder=5)

ax6.set_xlabel('Latency (seconds)', fontsize=11, fontweight='bold')
ax6.set_ylabel('Accuracy (%)', fontsize=11, fontweight='bold')
ax6.set_title('Accuracy-Latency Tradeoff', fontsize=12, fontweight='bold')
ax6.legend(fontsize=10, loc='lower right')
ax6.grid(True, alpha=0.3)

# ========================
# Row 3: Quality & Efficiency
# ========================

# 3.1: Spot-check quality scores
ax7 = fig.add_subplot(gs[2, 0])
quality_vals = [quality_scores[m] for m in methods]
bars = ax7.bar(methods, quality_vals, color=colors, alpha=0.7, edgecolor='black', linewidth=2)
ax7.set_ylabel('Quality Score (out of 5)', fontsize=11, fontweight='bold')
ax7.set_title('Answer Quality by Method (Spot-Check, n=20)', fontsize=12, fontweight='bold')
ax7.set_ylim([4.0, 5.0])
ax7.axhline(y=4.47, color='red', linestyle='--', linewidth=2, alpha=0.5, label='Overall Mean (4.47)')
ax7.grid(True, alpha=0.3, axis='y')
ax7.legend(fontsize=9)

for bar, val in zip(bars, quality_vals):
    height = bar.get_height()
    ax7.text(bar.get_x() + bar.get_width()/2., height + 0.02,
            f'{val:.2f}', ha='center', va='bottom', fontsize=10, fontweight='bold')

# 3.2: Efficiency metric (accuracy gain per latency increase)
ax8 = fig.add_subplot(gs[2, 1])
latency_increase_pct = [0, 23.9, 50.1]  # percent increase over baseline
accuracy_gain_pct = [0, 3.8, 25.7]  # percentage points
efficiency = [0 if lat == 0 else acc/lat for lat, acc in zip(latency_increase_pct, accuracy_gain_pct)]

method_labels_eff = ['Baseline', 'Performance', 'LLM']
colors_eff = ['gray', '#ff7f0e', '#2ca02c']

bars = ax8.bar(method_labels_eff, efficiency, color=colors_eff, alpha=0.7, edgecolor='black', linewidth=2)
ax8.set_ylabel('Accuracy Gain per % Latency', fontsize=11, fontweight='bold')
ax8.set_title('Routing Efficiency', fontsize=12, fontweight='bold')
ax8.grid(True, alpha=0.3, axis='y')

for bar, eff in zip(bars[1:], efficiency[1:]):  # Skip baseline
    height = bar.get_height()
    ax8.text(bar.get_x() + bar.get_width()/2., height + 0.01,
            f'{eff:.2f}pp/\u0025', ha='center', va='bottom', fontsize=10, fontweight='bold')

# 3.3: Stability (inverse of std dev)
ax9 = fig.add_subplot(gs[2, 2])
stability_data = {
    'Semantic': 0.0,
    'Performance': 1.5,
    'LLM': 0.6
}
stability_vals = [stability_data[m] for m in methods]
bars = ax9.bar(methods, stability_vals, color=colors, alpha=0.7, edgecolor='black', linewidth=2)
ax9.set_ylabel('Accuracy Std Dev (%pp)', fontsize=11, fontweight='bold')
ax9.set_title('Stability Across 5 Trials\n(Lower is Better)', fontsize=12, fontweight='bold')
ax9.set_ylim([0, 2])
ax9.grid(True, alpha=0.3, axis='y')

for bar, val in zip(bars, stability_vals):
    height = bar.get_height()
    if val > 0:
        ax9.text(bar.get_x() + bar.get_width()/2., height + 0.05,
                f'{val:.1f}pp', ha='center', va='bottom', fontsize=10, fontweight='bold')
    else:
        ax9.text(bar.get_x() + bar.get_width()/2., height + 0.05,
                'Perfect', ha='center', va='bottom', fontsize=9, fontweight='bold')

# Main title
fig.suptitle('Multi-Agent Routing: Comprehensive Results Analysis (5-Trial Evaluation)', 
             fontsize=16, fontweight='bold', y=0.995)

plt.savefig('c:\\Users\\KILNKX\\Desktop\\1508 project\\output\\results_comprehensive.png', 
           dpi=300, bbox_inches='tight', facecolor='white')
print("✓ Saved: results_comprehensive.png")

# ========================
# Figure 2: Agent Quality Breakdown
# ========================

fig2, axes = plt.subplots(1, 2, figsize=(14, 5))

# Agent quality scores
agent_names = ['DataEngAgent', 'StatisticsAgent', 'MLAgent', 'VizAgent']
agent_scores = [4.25, 4.71, 4.23, 4.67]
agent_counts = [4, 7, 6, 3]
agent_colors = ['#e74c3c', '#3498db', '#f39c12', '#9b59b6']

ax = axes[0]
bars = ax.barh(agent_names, agent_scores, color=agent_colors, alpha=0.7, edgecolor='black', linewidth=2)
ax.set_xlabel('Quality Score (out of 5)', fontsize=12, fontweight='bold')
ax.set_title('Answer Quality by Agent', fontsize=13, fontweight='bold')
ax.set_xlim([4.0, 5.0])
ax.grid(True, alpha=0.3, axis='x')

for i, (bar, score, count) in enumerate(zip(bars, agent_scores, agent_counts)):
    ax.text(score + 0.02, bar.get_y() + bar.get_height()/2.,
           f'{score:.2f} (n={count})', ha='left', va='center', fontsize=10, fontweight='bold')

# Quality dimensions
dimensions = ['Relevance', 'Domain Conf.', 'Completeness', 'Actionability', 'Correctness']
dim_scores = [4.60, 4.50, 4.45, 4.40, 4.40]
dim_colors = ['#27ae60', '#2980b9', '#f39c12', '#e74c3c', '#c0392b']

ax = axes[1]
bars = ax.barh(dimensions, dim_scores, color=dim_colors, alpha=0.7, edgecolor='black', linewidth=2)
ax.set_xlabel('Average Score (out of 5)', fontsize=12, fontweight='bold')
ax.set_title('Quality by Evaluation Dimension', fontsize=13, fontweight='bold')
ax.set_xlim([4.0, 5.0])
ax.grid(True, alpha=0.3, axis='x')

for bar, score in zip(bars, dim_scores):
    ax.text(score + 0.02, bar.get_y() + bar.get_height()/2.,
           f'{score:.2f}', ha='left', va='center', fontsize=10, fontweight='bold')

fig2.suptitle('Quality Evaluation Details (Spot-Check Analysis, n=20)', 
             fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig('c:\\Users\\KILNKX\\Desktop\\1508 project\\output\\quality_breakdown.png', 
           dpi=300, bbox_inches='tight', facecolor='white')
print("✓ Saved: quality_breakdown.png")

# ========================
# Figure 3: Method Comparison Summary
# ========================

fig3, axes = plt.subplots(2, 2, figsize=(14, 10))

# Method 1: Semantic
ax = axes[0, 0]
ax.text(0.5, 0.85, 'Method 1: Semantic Similarity', ha='center', fontsize=14, fontweight='bold',
       bbox=dict(boxstyle='round', facecolor='#1f77b4', alpha=0.3, edgecolor='black', linewidth=2))
metrics_semantic = [
    'Accuracy: 69.0% (±0.0%)',
    'In-Domain: 91.8% (±0.5%)',
    'Latency: 5.49s per query',
    'Routing Overhead: 11.5ms',
    'Quality Score: 4.41/5.0',
    'Stability: Perfect'
]
for i, metric in enumerate(metrics_semantic):
    ax.text(0.1, 0.7 - i*0.12, f'• {metric}', fontsize=11, verticalalignment='top', family='monospace')
ax.axis('off')

# Method 2: Performance
ax = axes[0, 1]
ax.text(0.5, 0.85, 'Method 2: Performance-Weighted', ha='center', fontsize=14, fontweight='bold',
       bbox=dict(boxstyle='round', facecolor='#ff7f0e', alpha=0.3, edgecolor='black', linewidth=2))
metrics_perf = [
    'Accuracy: 72.8% (±1.5%)',
    'In-Domain: 94.2% (±0.8%)',
    'Latency: 6.80s per query',
    'Routing Overhead: 12.0ms',
    'Quality Score: 4.50/5.0',
    'Improvement: +3.8pp accuracy'
]
for i, metric in enumerate(metrics_perf):
    ax.text(0.1, 0.7 - i*0.12, f'• {metric}', fontsize=11, verticalalignment='top', family='monospace')
ax.axis('off')

# Method 3: LLM
ax = axes[1, 0]
ax.text(0.5, 0.85, 'Method 3: LLM Meta-Classification', ha='center', fontsize=14, fontweight='bold',
       bbox=dict(boxstyle='round', facecolor='#2ca02c', alpha=0.3, edgecolor='black', linewidth=2))
metrics_llm = [
    'Accuracy: 94.7% (±0.6%)',
    'In-Domain: 99.2% (±0.2%)',
    'Latency: 8.24s per query',
    'Routing Overhead: 2410.6ms',
    'Quality Score: 4.53/5.0',
    'Improvement: +25.7pp accuracy'
]
for i, metric in enumerate(metrics_llm):
    ax.text(0.1, 0.7 - i*0.12, f'• {metric}', fontsize=11, verticalalignment='top', family='monospace')
ax.axis('off')

# Recommendations
ax = axes[1, 1]
ax.text(0.5, 0.95, 'Recommendations', ha='center', fontsize=14, fontweight='bold',
       bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.2, edgecolor='black', linewidth=2))
recommendations = [
    '✓ Use Semantic for: Low-latency use',
    '  cases, resource-constrained systems',
    '',
    '✓ Use Performance for: Balanced',
    '  accuracy-latency tradeoff with',
    '  continuous adaptation',
    '',
    '✓ Use LLM for: High-accuracy',
    '  scenarios where quality is critical',
]
for i, rec in enumerate(recommendations):
    ax.text(0.05, 0.85 - i*0.095, rec, fontsize=10, verticalalignment='top')
ax.axis('off')

fig3.suptitle('Method Comparison Summary', fontsize=15, fontweight='bold')
plt.tight_layout()
plt.savefig('c:\\Users\\KILNKX\\Desktop\\1508 project\\output\\method_comparison_summary.png', 
           dpi=300, bbox_inches='tight', facecolor='white')
print("✓ Saved: method_comparison_summary.png")

print("\n" + "="*60)
print("FIGURE GENERATION COMPLETE")
print("="*60)
print("\nGenerated 3 publication-quality figures:")
print("1. results_comprehensive.png - 9-panel comprehensive analysis")
print("2. quality_breakdown.png - Agent and dimension quality breakdown")
print("3. method_comparison_summary.png - Summary comparison and recommendations")
print("\nAll figures saved to: c:\\Users\\KILNKX\\Desktop\\1508 project\\output\\")
