# -*- coding: utf-8 -*-
"""
Created on Tue Jun 11 09:40:56 2024

@author: lucile.schulthe
"""
import numpy as np
import pandas as pd
import class_def_v5 as cdef
import math
import pickle
import c

gen_values =np.array( [7500, 7501, 7510, 7511,7512,7513, 7520,7530, 7540, 7541,   7542, 7543,7550,7560, 7570, 7580, 7581, 7582, 7598, 7599])
gen_data = ['unknow','hp', 'hp',  'hp','hp','hp','gas', 'oil','wood','wood','wood', 'wood', 'unknow', 'elec','solar','dh', 'dh', 'dh','unknow', 'unknow']
gwaerzh_values =np.array( [7400,7410,7411,7420,7421,7430,7431,7432,7433,7434,7435,7436,7440,7441,7450,7451,7452,7460,7461,7499])
gwaerzh_data =np.array( ['unknow','hp','hp','solar','solar','oil','oil','oil','oil','oil','oil','wood','oil','oil','elec','elec','elec','dh','dh','unknow'])

gwaerzw_values=np.array([7600,7610,7620,7630,7632,7634,7640,7650,7651,7660,7699])
gwaerzw_data=np.array(['unknow','hp','solar','oil','oil','oil','oil','elec','oil','dh','unknow'])

#%% ############# System ########################################
   
def heating_definition(ar,genh,genw,gwaerzh,gwaerzw,gebf):   
    if math.isnan(genh):
        if math.isnan(gwaerzh):
            genh=7500
            key='unknow'
        else:
            x = np.where(gwaerzh_values == gwaerzh)[0]
            key=gwaerzh_data[x[0]]        
    else :           
        x = np.where(gen_values == genh)[0]
        key=gen_data[x[0]]
        
    
    if key=='unknow' and not math.isnan(gwaerzh):
            x = np.where(gwaerzh_values == gwaerzh)[0]
            key=gwaerzh_data[x[0]]  

    ar.heatingsystem[key]+=gebf
    ar.heatingsystem_nb[key]+=1    
    ar.heatingsystem_nb_log[key]+=nb_log  
    
    if math.isnan(genw):
        if math.isnan(gwaerzw):
            keyw=key
        
        else:
            x = np.where(gwaerzw_values == gwaerzw)[0]
            keyw=gwaerzw_data[x[0]] 
        
    else :    
        x = np.where(gen_values == genw)[0]
        keyw=gen_data[x[0]]
        
    if keyw=='unknow':
        keyw=key
        

    ar.watersystem[keyw]+=gebf    
    ar.watersystem_nb[keyw]+=1  
    ar.watersystem_nb_log[keyw]+=nb_log

def init_house(house):
    
    for obj in house:
        obj.heatingsystem_nb = {}
        obj.heatingsystem_nb_log = {}
        obj.watersystem_nb = {}
        obj.watersystem_nb_log = {}
        for system, value in obj.heatingsystem.items():
            obj.heatingsystem[system] = 0  
            obj.heatingsystem_nb[system] = 0 
            obj.heatingsystem_nb_log[system] = 0   
            obj.watersystem[system] = 0
            obj.watersystem_nb[system] = 0 
            obj.watersystem_nb_log[system] = 0   
    
        obj.nb_log=0
        obj.eratot=0
        
def add_house(house):
        house[gbaup].nb += 1
        house[gbaup].nb_log += nb_log
        house[gbaup].eratot += warea
        heating_definition(house[gbaup],genh1,genw1,gwaerzh1,gwaerzw1,warea)

        
#%% ############### Import REGBL#################################

# import REGBL logement
path = "autre/wohnung_logement_abitazione.csv" 
df_logement = pd.read_csv(path, sep='\t', decimal='.', usecols=['EGID','WAREA','WSTAT'])
df_logement = df_logement[df_logement['WSTAT'] == 3004] # supprime les logements non existants

# import REGBL batiment
path = "autre/regbl_GEB.dsv"
df_batiment = pd.read_csv(path, sep='\t', decimal='.', usecols=['EGID','GEBF','GAREA','GASTW','GBAUP','GKLAS','GSTAT','GKAT','GENH1','GENW1','GWAERZH1','GWAERZW1','GBAUJ','GRENJ'])

# group logement par EGID
surface_totale_par_batiment  = df_logement.groupby('EGID').agg(surface_totale=('WAREA', 'sum'),nombre_occurences=('WAREA', 'size')).reset_index()
surface_totale_par_batiment.columns = ['EGID', 'Surface_Totale_Logements','nb_log']

# group logement + batiment par EGID
result_df = pd.merge(df_batiment, surface_totale_par_batiment, on='EGID', how='left')

# Supprime les bâtiments qui n'ont pas de logement ou inexistants
result_df = result_df.dropna(subset=['nb_log']) # enlève les bâtiments sans logements
result_df = result_df[result_df['GSTAT'] == 1004] # supprime les bâtiments non existants
result_df = result_df[result_df['GKAT'] != 1010] # supprime les bâtiments provisoires 

    #%% ############### Creation archetype #################################
SFH=[]
MFH=[]
MFH_tot=[]
MUA=[]
OTH=[]

path = "database/archetype.xlsx"        # reprends les archetypes d'alessandro
data = pd.read_excel(path)       

archetype_name=data['dataname'].values[1:10]
    
for name in archetype_name    :
    SFH.append(cdef.ArchData(name))   #one archetype per periode

archetype_name=data['dataname'].values[10:]
for name in archetype_name    :
    MFH.append(cdef.ArchData(name))   #one archetype per periode
    
for name in archetype_name    :
    MFH_tot.append(cdef.ArchData(name))   #one archetype per periode

for name in archetype_name    :
    MUA.append(cdef.ArchData(name))   #one archetype per periode   # reprends les archetypes d'alessandro selon MFH

for name in archetype_name    :
    OTH.append(cdef.ArchData(name))   #one archetype per periode   # reprends les archetypes d'alessandro selon MFH




#%% ############### Mettre à zero les valeurs du REGBL#################################

# supprime les valeurs des archetypes qui vont être remplacer par le REGBL et ajoute d'autre données
init_house(SFH)
init_house(MFH)
init_house(MFH_tot)
init_house(MUA)
init_house(OTH)

#%% ############### data en plus ################################
nb_log_nosurface=0 # nombre de logement sans surface de logement
nb_bat_nosurface=0 # nombre de bâtiment sans surface de logement
nb_bat_nogbaup=0

surface_suppl=0    # surface supplémentaire calculé
surface_suppl_moyen=0 # surface supplémentaire calculé sur une moyenne des logements

surface_moyenne=[96.4,92.2,83.8,83,93.1,106.8,112.1,(131.1+124.7)/2,(115+101.9)/2]
nb_nolog=0
nb_SFH=0
nb_MFH=0
nb_MUA=0
nb_OTH=0
nb_OAH=0


nb_SFH_log=0
nb_MFH_log=0
nb_MUA_log=0
nb_OTH_log=0
nb_OAH_log=0


su_SFH=0
su_MFH=0
su_MUA=0
su_OTH=0
su_OAH=0



    
#%% ############### Import REGBL#################################

for index, row in result_df.iterrows():

    
    gebf = row['GEBF']                  # sre
    gklas = row['GKLAS']                # 
    garea=row['GAREA']                  # surface au sol
    gastw=row['GASTW']                  # nb d'étage
    # gvol=row['GVOL']
    gstat=row['GSTAT']
    gkat=row['GKAT']
    warea=row['Surface_Totale_Logements']
    genh1=row['GENH1']
    genw1=row['GENW1'] 
    gwaerzh1=row['GWAERZH1']
    gwaerzw1=row['GWAERZW1']
    
    gwaerzw1=row['GWAERZW1']
    gbauj=row['GBAUJ']
    grenj=row['GRENJ']
    nb_log=row['nb_log']
    egid=row['EGID']    
    
    if math.isnan(row['GBAUP']): # les bâtiments sans période de construction sont jugés comme vieux (268 bâtiments)
        gbaup=0
        nb_bat_nogbaup+=1
    else:     
        gbaup = int(row['GBAUP'] - 8011)
    # genh2=row['GENH2']
    # genw2=row['GENW2'] 
    # gwaerzh2=row['GWAERZH2']
    # gwaerzw2=row['GWAERZW2']
    

    if gbaup==6 or gbaup==7:
        gbaup-=1
    elif gbaup==8 or gbaup==9:
        gbaup-=2
    elif  gbaup==10 or gbaup==11:
        gbaup-=3 
    elif gbaup==12:
        gbaup-=4
         
    

            
    if (math.isnan(warea) or warea==0):       
        nb_bat_nosurface+=1
        nb_log_nosurface+=nb_log
        
        if not (math.isnan(gebf) or gebf==0):
            warea=gebf
            surface_suppl+=warea
        elif not (math.isnan(garea) or garea==0 or math.isnan(gastw) or gastw==0): 
            warea=garea*gastw*0.8
            surface_suppl+=warea      
        else:
            warea=nb_log*surface_moyenne[gbaup]
            surface_suppl+=warea
            surface_suppl_moyen+=warea
        
    if (gklas==1110 and gkat == 1020 and nb_log==1):
        add_house(SFH)
        nb_SFH+=1
        nb_SFH_log+=nb_log
        su_SFH+=warea                
                
    elif ((gklas==1110 or gklas==1121 or gklas==1122) and (gkat == 1020)): 
       add_house(MFH)
       add_house(MFH_tot)
       nb_MFH+=1
       nb_MFH_log+=nb_log
       su_MFH+=warea
       
    elif (gkat == 1030): 
       add_house(MUA)
       add_house(MFH_tot)
       nb_MUA+=1
       nb_MUA_log+=nb_log
       su_MUA+=warea
    
    elif gkat == 1040:
        add_house(OTH)
        add_house(MFH_tot)
        nb_OTH+=1
        nb_OTH_log+=nb_log
        su_OTH+=warea 
        
    else :
        nb_OAH+=1
        nb_OAH_log+=nb_log
        su_OAH+=warea 
            
#    nb_bat_aveclog=nb_OTH+nb_SFH+nb_MFH
                
#%% ############### Divid by SRE or nb #################################    

town=[SFH,MFH, MUA,OTH]
town_simpl=[SFH,MFH_tot]

#%% 
# for building in town:
            
#     for obj in building:

#         for system, value in obj.heatingsystem.items():                                                                                                                 
#             divided_value = value / obj.eratot                                                           # Diviser la valeur par 'gebf'
#             obj.heatingsystem_pc[system] = divided_value                                                   # Mettre à jour la valeur dans le système de chauffage
        
#         for system, value in obj.watersystem.items():
#             divided_value = value / obj.eratot                                                         
#             obj.watersystem_pc[system] = divided_value    
            
#         obj.era=obj.eratot/obj.nb
        
#     obj.era=obj.eratot/obj.nb        

# #%% 

# with open('town_regbl.pkl', 'wb') as f:
#     pickle.dump(town, f)
    
    
    #%% 
for building in town_simpl:
            
    for obj in building:

        for system, value in obj.heatingsystem.items():                                                                                                                 
            divided_value = value / obj.eratot                                                           # Diviser la valeur par 'gebf'
            obj.heatingsystem[system] = divided_value                                                   # Mettre à jour la valeur dans le système de chauffage
        
        for system, value in obj.watersystem.items():
            divided_value = value / obj.eratot                                                         
            obj.watersystem[system] = divided_value    
            
        obj.era=obj.eratot/obj.nb
        
    obj.era=obj.eratot/obj.nb  
        
with open('town_simpl_regbl.pkl', 'wb') as f:
    pickle.dump(town_simpl, f)

#%% Write value
print(nb_SFH,nb_MFH,nb_MUA,nb_OTH,nb_OAH)
print(su_SFH,su_MFH,su_MUA,su_OTH,su_OAH)
print(nb_SFH_log,nb_MFH_log,nb_MUA_log,nb_OTH_log,nb_OAH_log)