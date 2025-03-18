# -*- coding: utf-8 -*-
"""
Created on Tue Sep  3 14:02:04 2024

@author: lucile.schulthe
"""


import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
import numpy as np
from cycler import cycler
import plotly.io as pio
import plotly.tools as tls
from IPython.display import HTML

plt.rcParams['lines.markersize'] = 6           # Taille des marqueurs
plt.rcParams['lines.markeredgewidth'] = 0.5    # Épaisseur du bord des marqueurs
plt.rcParams['lines.linewidth'] = 1.5            # Épaisseur des lignest
plt.rcParams['grid.color'] = 'lightgrey' 
plt.rcParams['axes.grid'] = True
#plt.style.use('grayscale')

#colors = ['black','grey','silver','gainsboro']
#colors = ['0','0.4','0.8','0.9']
colors = ['0','0.4','0.6','0.7','0.4','0.6']
# Modification du cycle de couleur en dégradé de gris
plt.rcParams['axes.prop_cycle'] = cycler(color=colors)


def parallel_coordinate(combinations,combinations_name, variable_name,result,name,result_color):
    dict_list=[]
    
    it_surf=0
    for it in range(len(variable_name)):
        df = pd.DataFrame({variable_name[it]: [f[it] for f in combinations]})
        valeurs_uniques = df[variable_name[it]].astype(str).unique()
        dict_list.append(dict(range=[min(df[variable_name[it]]), max(df[variable_name[it]])], tickvals =valeurs_uniques,ticktext=combinations_name[it], label=variable_name[it], values=df[variable_name[it]]))
        
        
    for it_res in range(len(result)):
        if result[it_res].ndim>1:
            sum_res= np.sum(result[it_res],axis=0)
        else:
            sum_res=result[it_res]
        df_res = pd.DataFrame({'Result': sum_res})    
#        dict_list.append(dict(range=[min(sum_res), max(sum_res)], label=name[it_res], values=df_res['Result']))
        if it_surf <3:
            dict_list.append(dict(range=[0, 500],tickvals=list(range(0, 501, 50)), label=name[it_res], values=df_res['Result']))
        else:
            dict_list.append(dict(range=[0, 70],tickvals=list(range(0, 71, 10)), label=name[it_res], values=df_res['Result']))
        
        it_surf+=1
    if result_color.ndim>1:
        result_color= np.sum(result_color,axis=0)
    else:
        pass
        
    # Créez le graphique Parallel Coordinates interactif avec plotly
    fig = make_subplots(rows=1, cols=1)
    fig.add_trace(
        go.Parcoords(
            line=dict(color=result_color, colorscale=[[0, 'rgb(0, 176, 80)'],[0.5, 'rgb(255, 192,0)'],[1, 'rgb(255, 0,0)']], showscale=True),  # Utilisez cauto=True pour ajuster automatiquement l'épaisseur des courbes
            dimensions=dict_list,
            unselected = dict(line = dict(color = 'white', opacity = .1))
        )
    )


    # Enregistrez le graphique dans un fichier HTML
    fig.write_html("graphique_parallel_coordinates.html")

    # Ouvrez le fichier HTML dans votre navigateur
    import webbrowser
    webbrowser.open("graphique_parallel_coordinates.html", new=2)
    
    
    
def evolution(years_init,liste,name,ylabel,title,subtitle,style,tempmarker,years_end=2051):
    plt.figure(dpi=150)
    year_plot=np.arange(years_init,years_end,1)
    year_xtick=np.arange(years_init+6,years_end,10)
    l_plot=years_end-years_init
    plt.ion()
    i=0
    
    for evol in liste:
        plt.plot(year_plot,evol[:l_plot],linestyle=style[i],marker=tempmarker[i])
        i+=1
        if len(style)<i+1:
            style.append(style[i-1])
        if len(tempmarker)<i+1:
            tempmarker.append(tempmarker[i-1])
    plt.legend(name)
    plt.xlabel('years')
    plt.ylabel(ylabel)

    plt.suptitle(title, y=1, fontsize=15)
    plt.title(subtitle, fontsize=10)
    plt.xlim(left=years_init, right=years_end-1)
    plt.ylim(bottom=0)    
#    plt.xticks(np.append(years_init,year_xtick))
    plt.show()
    
#     plotly_fig = tls.mpl_to_plotly(plt.gcf())

# # Afficher le graphique en HTML
#     fig_html = pio.to_html(plotly_fig, full_html=False)
#     plt.close()  # Fermer la figure Matplotlib pour libérer la mémoire
    
def evolution2(years_init,liste,liste2,name,ylabel,title,subtitle,style,tempmarker,years_end=2051):
    year_plot=np.arange(years_init,years_end,1)
    l_plot=years_end-years_init
    fig, ax1 = plt.subplots(dpi=150)
    i=0    
    for evol in liste:
        ax1.plot(year_plot,evol[:l_plot],label=name[i],linestyle=style[i],marker=tempmarker[i])
        i+=1
        if len(style)<i+1:
            style.append(style[i-1])
        if len(tempmarker)<i+1:
            tempmarker.append(tempmarker[i-1])
    plt.ylabel(ylabel[0])        
    ax2 = ax1.twinx()   
    ax2.set_ylabel('Y2', color='gray')
    ax2.tick_params(axis='y', colors='gray')       # Couleur des graduations
    ax2.spines['right'].set_color('gray')          # Couleur de la bordure de l'axe droit
    ax2.yaxis.label.set_color('gray')              # Couleur du label de l'axe Y
    for evol in liste2:
        ax2.plot(year_plot,evol[:l_plot], color='gray',label=name[i],linestyle=style[i],marker=tempmarker[i])
        i+=1
        if len(style)<i+1:
            style.append(style[i-1])
        if len(tempmarker)<i+1:
            tempmarker.append(tempmarker[i-1])
        
    ax2.grid(False)
    plt.xlabel('years')
    plt.ylabel(ylabel[1])
    plt.suptitle(title, y=1, fontsize=15)
    plt.title(subtitle, fontsize=10)
    plt.xlim(left=years_init, right=years_end-1)
    plt.ylim(bottom=0)  
    year_xtick=np.arange(years_init+6,years_end,10)
#    plt.style.use("grayscale")

#    plt.xticks(np.append(years_init,year_xtick))
    

    

    
def evolution_neg(years_init,liste,name,ylabel,title,subtitle,style,tempmarker,years_end=2051):
    year_plot=np.arange(years_init,years_end,1)
    l_plot=years_end-years_init
    plt.figure(dpi=150)

    i=0
    for evol in liste:
        plt.plot(year_plot,evol[:l_plot],linestyle=style[i],marker=tempmarker[i])
        i+=1
        if len(style)<i+1:
            style.append(style[i-1])
        if len(tempmarker)<i+1:
            tempmarker.append(tempmarker[i-1])
    plt.legend(name)
    plt.xlabel('years')
    plt.ylabel(ylabel)
    plt.suptitle(title, y=1, fontsize=15)
    plt.title(subtitle, fontsize=10)
    plt.xlim(left=years_init, right=years_end-1)
    # year_xtick=np.arange(years_init+6,years_end,10)
    # plt.xticks(np.append(years_init,year_xtick))

  
        
    
    
def cumul(years_init,liste,name,ylabel,title,subtitle,style,tempmarker,years_end=2051):
    
    year_plot=np.arange(years_init,years_end,1)
    l_plot=years_end-years_init
    plt.figure(dpi=150)
#    print(name)
    i=0
    for evol in liste:
        cumulative_sum=np.cumsum(evol[:l_plot])
        plt.plot(year_plot,cumulative_sum[:l_plot],linestyle=style[i],marker=tempmarker[i])
        i+=1
        if len(style)<i+1:
            style.append(style[i-1])
        if len(tempmarker)<i+1:
            tempmarker.append(tempmarker[i-1])
            
#☻        print(cumulative_sum[l_plot-1])
    plt.legend(name)
    plt.xlabel('years')
    plt.ylabel(ylabel)
    plt.suptitle(title, y=1, fontsize=15)
    plt.title(subtitle, fontsize=10)    
    plt.xlim(left=years_init, right=years_end-1)
    year_xtick=np.arange(years_init+6,years_end,10)
#    plt.xticks(np.append(years_init,year_xtick))    
    
def bar(years_init,liste,name,ylabel,title,subtitle,style,tempmarker,years_end=2051):
    year_plot=np.arange(years_init,years_end,1)
    l_plot=years_end-years_init
    plt.figure(dpi=150)
    i=0
    for evol in liste:

        plt.plot(year_plot,evol[:l_plot],linestyle=style[i],marker=tempmarker[i])
        i+=1
        if len(style)<i+1:
            style.append(style[i-1])

    plt.xlabel('years')
    plt.ylabel(ylabel)
    plt.legend(name)
    plt.suptitle(title, y=1, fontsize=15)
    plt.title(subtitle, fontsize=10)    
    plt.xlim(left=years_init, right=years_end-1)  
    year_xtick=np.arange(years_init+6,years_end,10)
    plt.xticks(np.append(years_init,year_xtick))    
    
def bar_cumul(years_init,liste,name,ylabel,title,subtitle,style,tempmarker,years_end=2051):

    year_plot=np.arange(years_init,years_end,1)
    l_plot=years_end-years_init
    plt.figure(dpi=150)
    i=0
    bar_width = 0.7

    val = np.zeros(l_plot)
    for it_val in liste:
        plt.bar(year_plot,it_val[:l_plot], width=bar_width,bottom=val,linestyle=style[i])
        
        val+=it_val[:l_plot]
        i+=1
        if len(style)<i+1:
            style.append(style[i-1])

    
    plt.legend(name,loc="upper center", bbox_to_anchor=(0.5, -0.12), ncol=2)

#    plt.tight_layout()
    plt.xlabel('years')
    plt.ylabel(ylabel)
    plt.suptitle(title, y=1, fontsize=15)
    plt.title(subtitle, fontsize=10)
    plt.xlim(left=years_init, right=years_end-1)  
#    year_xtick=np.arange(years_init+6,years_end,10)
#    plt.xticks(np.append(years_init,year_xtick)) 

def bar_cumul_neg(years_init,liste,name,ylabel,title,subtitle,style,tempmarker,years_end=2051):
    # colors = ['0','0.4','0.9','0','0.4','0.6']
    # plt.rcParams['axes.prop_cycle'] = cycler(color=colors)

    year_plot=np.arange(years_init,years_end,1)
    l_plot=years_end-years_init
    plt.figure(dpi=150)
    i=0
    bar_width = [0.7,0.5,0.4]

    val = np.zeros(l_plot)
    for it_val in liste:
        plt.bar(year_plot,it_val[:l_plot], width=bar_width[i],bottom=val,linestyle=style[i])
        
#        val+=it_val[:l_plot]
        i+=1
        if len(style)<i+1:
            style.append(style[i-1])

    
    plt.legend(name)

#    plt.tight_layout()
    plt.xlabel('years')
    plt.ylabel(ylabel)
    plt.suptitle(title, y=1, fontsize=15)
    plt.title(subtitle, fontsize=10)
    plt.xlim(left=years_init, right=years_end-1)  
#    year_xtick=np.arange(years_init+6,years_end,10)
#    plt.xticks(np.append(years_init,year_xtick))   
  

def bar_cumul_cumul(years_init,liste,name,ylabel,title,subtitle,style,tempmarker,years_end=2051):
    year_plot=np.arange(years_init,years_end,1)
    l_plot=years_end-years_init
    plt.figure(dpi=150)
    
    bar_width = 0.7
    i=0
    val = np.zeros(l_plot)
    for evol in liste:
        it_val=np.cumsum(evol[:l_plot])
        plt.bar(year_plot,it_val[:l_plot], width=bar_width,bottom=val)
        
        val+=it_val[:l_plot]
        i+=1
        if len(style)<i+1:
            style.append(style[i-1])
        if len(tempmarker)<i+1:
            tempmarker.append(tempmarker[i-1])

    
    plt.legend(name)
    plt.xlabel('years')
    plt.ylabel(ylabel)
    plt.suptitle(title, y=1, fontsize=15)
    plt.title(subtitle, fontsize=10) 
    plt.xlim(left=years_init, right=years_end-1)  
    year_xtick=np.arange(years_init+6,years_end,10)
    plt.xticks(np.append(years_init,year_xtick))       
    
    
def bar_cumul2(years_init,liste,liste2,name,ylabel,title,subtitle,style,tempmarker,years_end=2051):
    year_plot=np.arange(years_init,years_end,1)
    l_plot=years_end-years_init
    plt.figure(dpi=150)
    i=0
    bar_width = 0.8

    val = np.zeros(l_plot)
    for it_val in liste:
        plt.bar(year_plot,it_val[:l_plot], width=bar_width,bottom=val)
        
        val+=it_val[:l_plot]
        i+=1
        if len(style)<i+1:
            style.append(style[i-1])

        
    val = np.zeros(l_plot)
    for it_val in liste2:
        plt.bar(year_plot,it_val[:l_plot], width=bar_width,bottom=val)
        
        val+=it_val[:l_plot]
        i+=1
        if len(style)<i+1:
            style.append(style[i-1])
    
    plt.legend(name)
    plt.xlabel('years')
    plt.ylabel(ylabel)
    plt.suptitle(title, y=1, fontsize=15)
    plt.title(subtitle, fontsize=10)
    plt.xlim(left=years_init, right=years_end-1)  
    year_xtick=np.arange(years_init+6,years_end,10)
    plt.xticks(np.append(years_init,year_xtick))   
    
    
    
def evolutionplotly(years_init, liste, name, ylabel, title,subtitle,style,tempmarker, years_end=2051):
    year_plot = np.arange(years_init, years_end, 1)
    l_plot = years_end - years_init

    # Créer une figure Plotly
    fig = go.Figure()

    # Ajouter les traces
    for evol, label in zip(liste, name):
        fig.add_trace(go.Scatter(x=year_plot, y=evol[:l_plot], mode='lines+markers', name=label))

    # Mettre à jour la mise en forme de la figure
    fig.update_layout(
        title=title,
        xaxis_title='Years',
        yaxis_title=ylabel,
        xaxis=dict(
            range=[years_init, years_end-1],
            tickvals=np.append(years_init, np.arange(years_init + 6, years_end, 10))
        ),
        yaxis=dict(range=[0, None]),
        hovermode='x unified'
    )

    # Afficher la figure
    fig.show()