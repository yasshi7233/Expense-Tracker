import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import base64

# Warm, modern, cohesive finance palette
PALETTE = ['#0F766E', '#2563EB', '#D97706', '#E11D48', '#7C3AED', '#0284C7', '#059669', '#64748B']

def make_pie_chart(categories, amounts):
    if not categories:
        return None
    fig, ax = plt.subplots(figsize=(6, 4.5), facecolor='#FFFFFF')
    ax.set_facecolor('#FFFFFF')

    wedges, texts, autotexts = ax.pie(
        amounts,
        labels=categories,
        autopct='%1.1f%%',
        colors=PALETTE[:len(categories)],
        startangle=140,
        wedgeprops=dict(width=0.7, edgecolor='#FFFFFF', linewidth=2)
    )
    for text in texts:
        text.set_fontsize(9)
        text.set_color('#243447')
        text.set_fontweight('medium')
    for text in autotexts:
        text.set_fontsize(8.5)
        text.set_color('#FFFFFF')
        text.set_fontweight('bold')

    ax.set_title('Spending by Category', fontsize=12, fontweight='bold', color='#243447', pad=12)
    plt.tight_layout()
    return _encode_chart(fig)

def make_bar_chart(months, incomes, expenses):
    if not months:
        return None
    fig, ax = plt.subplots(figsize=(7.5, 4.5), facecolor='#FFFFFF')
    ax.set_facecolor('#FFFFFF')

    x = range(len(months))
    width = 0.35
    ax.bar([i - width/2 for i in x], incomes, width, label='Income', color='#0F766E', alpha=0.9, edgecolor='none', zorder=3)
    ax.bar([i + width/2 for i in x], expenses, width, label='Expense', color='#E11D48', alpha=0.9, edgecolor='none', zorder=3)

    ax.set_ylabel('Amount (Rs.)', fontsize=9.5, color='#64748B')
    ax.set_title('Monthly Income vs Expense', fontsize=12, fontweight='bold', color='#243447', pad=12)
    ax.set_xticks(list(x))
    ax.set_xticklabels(months, rotation=20, ha='right', fontsize=9, color='#243447')
    ax.tick_params(axis='y', colors='#64748B', labelsize=8.5)

    ax.legend(frameon=False, fontsize=9, loc='upper left')
    ax.yaxis.grid(True, linestyle='-', color='#F1F5F9', alpha=1.0, zorder=0)
    ax.set_axisbelow(True)

    # Hide top and right spines
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#E2E8F0')
    ax.spines['bottom'].set_color('#E2E8F0')

    plt.tight_layout()
    return _encode_chart(fig)

def _encode_chart(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight', dpi=130, facecolor=fig.get_facecolor(), edgecolor='none')
    buf.seek(0)
    encoded = base64.b64encode(buf.read()).decode('utf-8')
    plt.close(fig)
    return encoded
