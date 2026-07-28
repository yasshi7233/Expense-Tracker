import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt 
import io
import base64

def make_pie_chart(categories, amounts):
    if not categories:
        return None
    fig,ax = plt.subplots(figsize=(6,5))
    colors = ['#3498DB','#E74C3C','#2ECC71','#F39C12',
	              '#9B59B6','#1ABC9C','#E67E22','#95A5A6']
    wedges,texts,autotexts =ax.pie(
       amounts,
       labels= categories,
       autopct='%1.1f%%',
       colors =colors[:len(categories)],
       startangle=140
    )
    for text in autotexts:
       text.set_fontsize(9)
    ax.set_title('Spending by Category', fontsize=13, fontweight ='bold',pad=15)
    plt.tight_layout()
    return _encode_chart(fig)

def make_bar_chart(months,incomes,expenses):
   if not months:
      return None
   fig,ax=plt.subplots(figsize =(8,5))
   x = range(len(months))
   width =0.35
   ax.bar([i -width/2 for i in x], incomes,width,label='Income', color ='#2ECC71' , alpha =0.85)
   ax.bar([i +width/2 for i in x], expenses,width,label='Expense',color ='#E74C3C',alpha =0.85)
   ax.set_xlabel('Month')
   ax.set_ylabel('Amount(Rs.)')
   ax.set_title('Monthly Income vs Expense', fontsize =13, fontweight ='bold')
   ax.set_xticks(list(x))
   ax.set_xticklabels(months,rotation =30, ha='right')
   ax.legend()
   ax.yaxis.grid(True, linestyle ='--', alpha =0.7)
   ax.set_axisbelow(True)
   plt.tight_layout()
   return _encode_chart(fig)

def _encode_chart(fig):
   buf= io.BytesIO()
   fig.savefig(buf,format='png', bbox_inches ='tight',dpi=120)
   buf.seek(0)
   encoded = base64.b64encode(buf.read()).decode('utf-8')
   plt.close(fig)
   return encoded