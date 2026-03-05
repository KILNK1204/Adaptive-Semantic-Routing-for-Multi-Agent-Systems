import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.table import Table
import numpy as np

methods = ['Method 1:\nSemantic', 'Method 2:\nPerformance', 'Method 3:\nLLM']
accuracy = ['69.0 ± 0.0%', '72.8 ± 1.5%', '94.7 ± 0.6%']
in_domain = ['91.8 ± 0.5%', '94.2 ± 0.8%', '99.2 ± 0.2%']
stability = ['Perfect', 'Good', 'Excellent']

# Numerical values for coloring
acc_values = [69.0, 72.8, 94.7]
colors = ['#ffcccc', '#ffffcc', '#ccffcc']  # Light red to light green gradient

# Create figure and axis
fig, ax = plt.subplots(figsize=(12, 6))
ax.axis('tight')
ax.axis('off')

# Table data
table_data = [
    ['Method', 'Accuracy', 'In-Domain Rate', 'Stability'],
    [methods[0], accuracy[0], in_domain[0], stability[0]],
    [methods[1], accuracy[1], in_domain[1], stability[1]],
    [methods[2], accuracy[2], in_domain[2], stability[2]]
]

# Create table
table = ax.table(cellText=table_data, cellLoc='center', loc='center',
                colWidths=[0.2, 0.25, 0.25, 0.2])

# Style the table
table.auto_set_font_size(False)
table.set_fontsize(11)
table.scale(1, 3)

# Header styling
for i in range(4):
    cell = table[(0, i)]
    cell.set_facecolor('#4472C4')
    cell.set_text_props(weight='bold', color='white', fontsize=12)

# Row styling with color gradient
for i in range(1, 4):
    for j in range(4):
        cell = table[(i, j)]
        cell.set_facecolor(colors[i-1])
        cell.set_text_props(fontsize=11)
        if j == 0:
            cell.set_text_props(weight='bold', fontsize=11)

# Add title
plt.title('Routing Accuracy Results\nFive-Trial Evaluation (Mean ± Std Dev)', 
          fontsize=14, weight='bold', pad=20)

# Add footer with interpretation
fig.text(0.5, 0.02, 
         'Method 2 offers 3.8pp improvement over baseline while maintaining computational efficiency.\n' +
         'Method 3 achieves near-perfect accuracy (94.7%) at higher computational cost.',
         ha='center', fontsize=10, style='italic', wrap=True)

plt.tight_layout(rect=[0, 0.08, 1, 1])
plt.savefig('accuracy_results_table.png', dpi=300, bbox_inches='tight', facecolor='white')
print("✓ Saved: accuracy_results_table.png")
plt.close()

# Create a second table with additional metrics
fig, ax = plt.subplots(figsize=(14, 7))
ax.axis('tight')
ax.axis('off')

# Extended table data
extended_data = [
    ['Method', 'Accuracy', 'In-Domain', 'Routing (ms)', 'Total (s)', 'Quality (5pts)'],
    ['Semantic', '69.0±0.0%', '91.8±0.5%', '11.5', '5.49', '4.41'],
    ['Performance', '72.8±1.5%', '94.2±0.8%', '12.0', '6.80', '4.50'],
    ['LLM', '94.7±0.6%', '99.2±0.2%', '2410.6', '8.24', '4.53']
]

table2 = ax.table(cellText=extended_data, cellLoc='center', loc='center',
                 colWidths=[0.15, 0.15, 0.15, 0.15, 0.15, 0.15])

table2.auto_set_font_size(False)
table2.set_fontsize(11)
table2.scale(1, 3.5)

# Header styling
for i in range(6):
    cell = table2[(0, i)]
    cell.set_facecolor('#2F5496')
    cell.set_text_props(weight='bold', color='white', fontsize=11)

# Row styling
row_colors = ['#e7f0f7', '#fef2cc', '#d4edda']
for i in range(1, 4):
    for j in range(6):
        cell = table2[(i, j)]
        cell.set_facecolor(row_colors[i-1])
        cell.set_text_props(fontsize=10)
        if j == 0:
            cell.set_text_props(weight='bold', fontsize=11)

# Add title
plt.title('Comprehensive Results Summary\nAccuracy, Efficiency, and Quality Metrics', 
          fontsize=14, weight='bold', pad=20)

# Add footer
fig.text(0.5, 0.02, 
         'Method 2 (Performance-Weighted) achieves the best accuracy-efficiency balance: 0.16pp per percent latency.\n' +
         'Method 3 (LLM Meta) achieves highest accuracy but requires 200× routing overhead.',
         ha='center', fontsize=10, style='italic')

plt.tight_layout(rect=[0, 0.08, 1, 1])
plt.savefig('comprehensive_results_table.png', dpi=300, bbox_inches='tight', facecolor='white')
print("✓ Saved: comprehensive_results_table.png")
plt.close()

print("\nBoth tables generated successfully!")
