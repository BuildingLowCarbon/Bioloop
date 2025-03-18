# -*- coding: utf-8 -*-
"""
Created on Fri Apr 12 11:38:36 2024

@author: lucile.schulthe
"""

import graph_function_v2 as gr
import numpy as np
import pandas as pd
import class_def_v5 as cdef
import copy
from timeit import default_timer as timer
import pickle

# %% Function


def Renovation(bat, rate_ren):
    Heatingsystem_evolution(bat.archetype.heatingsystem, rate_ren)
    # Chaudiere à mazout et à gaz sont remplacées par de heatpump
    Heatingsystem_evolution(bat.archetype.watersystem, rate_ren)
    Heatingconsum_evolution(bat.archetype, rate_ren)

# heating system evolution: if gas or oil --> become hp (but maximum transformation rate)


# Chaudiere à mazout et à gaz sont remplacées par de heatpump
def Heatingsystem_evolution(system, rate):
    a = system['gas'] + system['hp']+system['oil']
    b = system['gas']+system['oil']
    if b > rate:
        system['gas'] -= rate*system['gas']/b
        system['oil'] -= rate*system['oil']/b
        system['hp'] = a-system['gas']-system['oil']

    else:
        system['hp'] = a
        system['gas'] = 0
        system['oil'] = 0

# consomtion evolution, a rate of the entire parc become more efficient


def Heatingconsum_evolution(arch, rate):

    # TODO séparer entre déjà reno et pas reno
    arch.reno = arch.eratot*(rate)
    consum_ren = 1.5*arch.Qh_li  # norm SIA Qh_li est uniquement la valeur du chauffage. L'ECS n'est pas compris dedans
    if (consum_ren < arch.heat_tot):  # if the renovation is more efficient than actual archetype
        arch.heat = arch.heat*(1-rate)+consum_ren*(rate)
        arch.heat_tot = arch.heat+arch.heat_water

    # else:
    #     print(arch.name)


def Import_scenario(path_list, scenario_name):
    scenario = []
    for path in path_list:
        line = []
        for name in scenario_name:
            scenario1 = cdef.Scenario(name)
            scenario1.set_data(path)
            line.append(scenario1)
        scenario.append(line)  # set the data from excel
    return scenario

def Import_scenario_mix(path_list, scenario_name,demval):
    scenario = []
    for path in path_list:
        line = []
        for name in scenario_name:
            scenario1 = cdef.Scenario_mix(name)
            if demval==60:
                scenario1.set_data_str(path)
            else :
                scenario1.set_data_reno(path)                
            line.append(scenario1)
        scenario.append(line)  # set the data from excel
    return scenario

def Create_town(scenario, archetype):
    town_list = []
    for j in range(len(scenario[0])):
        bat = []
        for ar in archetype:
            if ar.name[0] == 'S':
                bat.append(cdef.Building(scenario[0][j], ar))
            elif ar.name[0] == 'M':
                bat.append(cdef.Building(scenario[1][j], ar))
        town_list.append(cdef.Town(copy.deepcopy(bat)))

    ########### create town (list of building with characteristic/functions) ####################################################################################
    for town in town_list:
        # init surfaces
        town.set_init_surface(1)

    return town_list


def Init_town(town_init, out_all, out_permat, out_mat):
    for town in town_init:
        for i in out_all:
            # sum the outcome of each surface per each building and put in the bat.surface['total'] and not in the differents surfaces (but per phase)
            town.calcul_per_allmat(i)

        for j in out_permat:
            if j not in out_all:
                # sum the outcome of each surface per each building
                town.calcul_per_allmat(j)


def Init_Impact_Result(out_all, out_mat, out_permat, lsimu):
    surface = cdef.Surface()
    for keypha in surface.phase.keys():
        surface.phase[keypha].data_time = {}
    surface.data_time = {}
    surface.material = {}

    for i in out_all:
        for keypha in surface.phase.keys():
            # create in the town a variable to put the result per phase for each outcome
            surface.phase[keypha].data_time[i] = np.zeros((lsimu), dtype='f')
        # create in the town a variable to put the result per phase for each outcome
        surface.data_time[i] = np.zeros((lsimu), dtype='f')

    for l in out_mat:
        surface.material[l] = cdef.Material()
        surface.material[l].data_time = {}

        for keypha in surface.phase.keys():
            # create in the town a variable to put the result per phase for each outcome
            surface.phase[keypha].material[l].data_time = {}

    for j in out_permat:
        for l in out_mat:
            for keypha in surface.phase.keys():
                # create in the town a variable to put the result per phase for each outcome
                surface.phase[keypha].material[l].data_time[j] = np.zeros(
                    (lsimu), dtype='f')
            surface.material[l].data_time[j] = np.zeros((lsimu), dtype='f')
    return surface


def save_before_ren(town):
    for it_town in town:
        for bat in it_town.bat:
            bat.archetype.heatingsystem_init = copy.deepcopy(
                bat.archetype.heatingsystem)
            bat.archetype.watersystem_init = copy.deepcopy(
                bat.archetype.watersystem)
            bat.archetype.heat_init = copy.deepcopy(bat.archetype.heat)
            bat.archetype.heat_water_init = copy.deepcopy(
                bat.archetype.heat_water)


def reinit_ren(bat):
    bat.eratot = copy.deepcopy(bat.archetype.eratot)
    bat.archetype.heatingsystem = copy.deepcopy(
        bat.archetype.heatingsystem_init)
    bat.archetype.watersystem = copy.deepcopy(bat.archetype.watersystem_init)
    bat.archetype.heat = copy.deepcopy(bat.archetype.heat_init)
    bat.archetype.heat_water = copy.deepcopy(bat.archetype.heat_water_init)
    
    
    
def linear_interpolate(start, end, alpha):

    start_np = np.array(start)
    end_np = np.array(end)
    
    # Vérification pour s'assurer que les deux tableaux ont la même forme
    if start_np.shape != end_np.shape:
        raise ValueError("Error")

    # Calcul de l'interpolation linéaire
    return (1 - alpha) * start_np + alpha * end_np


# %% Class


class Result:
    def __init__(self, lsimu=0, variante=0, syst=0):
        self.tot = np.zeros(variante, dtype='f')
        self.time = np.zeros((lsimu, variante), dtype='f')
        if syst > 1:
            self.syst = np.zeros((lsimu, syst, variante), dtype='f')

    def __add__(self, autre_objet):
        return cdef.addition_obj(self, autre_objet)

    def time_sum(self):
        self.time = np.sum(self.syst, axis=1)

    def var_sum(self):
        self.tot = np.sum(self.time, axis=0)


# %% ############## Timer #############################################################################################################
start = timer()


# %% ############## INIT ##############################################################################################################
################# INPUT ##############################################################################################
population_init = 8960800    # Swiss population in 2024

years_init = 2024             # Years of init data
# Years data in future (+1 to include the last years)
years_sim = 2201
years_stop = 2051   # leave it at 2051
years_analyse=2051
############### Building Variable ##############################################################################################
time_deep = 30                                          # number of years before maintenance

time_dem = 60                                           # number of years before end of lige of material
time_ren = 30                                           # number of years before partial renovation

rate_SvsM=[0.131,0.869]                                 # rate between SFH and MFH in the new construction
rate_tran=0.1                                           # rate of new surface thanks to transformation or #var_rate_tran=np.array([0,0.1,0.2])     
      
rate_scen_init=[0,0.1,0.9]                              # rate of init scenario
rate_ren_init=0.01
rate_dem_init=0.001
       
var_rate_ren=np.array([0.01, 0.03,0.05])                # renovation rates
var_rate_dem=np.array([0.001,0.003,0.005])              # demolition rates
var_rate_scenario=np.array([[1,0,0],                    # rate of each scenario
                             [1/3,1/3,1/3],
                             [0,0.1,0.9]])


var_rate_m2_per_hab=np.array([0.85*53.5,53.5,59.5])     # m2 per habitant at the end of the simulation (linear evolution) (hypothese 15% de; strategie 2050, )
var_temps50=[2030,2035,2040,2045]                       # year of 50% of the final result (two linear evolution)


############### combination for the simulation ########################################################################################
combinations = [(f0,f1,f2,f3,f4) for f0 in var_rate_ren for f1 in var_rate_dem for f2 in var_rate_scenario for f3 in var_rate_m2_per_hab for f4 in var_temps50] # combinations of all data
var=len(combinations)

# for the graphics:
var_scenario_name=['Optimistic','Medium','BAU']
variable_name=['Renovation rate','Demolition rate','Scenario','m2 per hab','Year 50%']                               #variable name for graphics

combinations_data = [(f0,f1,f2,f3,f4)for f0 in var_rate_ren for f1 in var_rate_dem for f2 in np.arange(len(var_rate_scenario)) for f3 in var_rate_m2_per_hab for f4 in var_temps50] # combinations of all data
combinations_name =[var_rate_ren,var_rate_dem,var_scenario_name,var_rate_m2_per_hab,var_temps50]
 

############### Outcome ##############################################################################################

# to reduce the simulation time, not all variables are calculated but only the useful
outcome = ['gwp','gwp2050','gwpdyn', 'bio','bio0']                       # variable global
# variable calculated for each material
outcome_permat = ['kg']
outcome_mat = ['timber', 'concrete','vegetal_fiber']           # calculated material


# %% ############## DATA ##############################################################################################################
################ data Simu ##############################################################################################
l_simu = years_sim-years_init  # simulation length
l_inter = years_stop-years_init  # simulation length
l_2050=2051-years_init
l_analyse=years_analyse-years_init
# temporal frame of study years_init - years_sim
years = np.arange(years_init, years_sim, 1)
yearsbegin=years_init-time_deep

rate_time=np.zeros(l_simu+60, dtype='f')
for it_time in range(l_simu+60):
    np.zeros((l_simu, var), dtype='f')
    rate_temp=it_time/(l_inter-1)
    if rate_temp>1:
        rate_temp=1
    rate_time[it_time]=rate_temp
    
    
time_shift = {
    'construction': [np.zeros(0, dtype='f'), np.zeros(time_dem, dtype='f')],
    'maintenance20': [np.zeros(20, dtype='f'), np.zeros(time_dem-20, dtype='f')],
    'maintenance30': [np.zeros(30, dtype='f'), np.zeros(time_dem-30, dtype='f')],
    'maintenance40': [np.zeros(40, dtype='f'), np.zeros(time_dem-40, dtype='f')],
    'demolition': [np.zeros(time_dem, dtype='f'), np.zeros(0, dtype='f')],
    'time10': [np.zeros(10, dtype='f'), np.zeros(10, dtype='f')]
}
################ data Input ###############################################################################################
path = "database/data_input.xlsx"
data_input = pd.read_excel(path, decimal='.')
pop_rate = data_input['pop_rate'].values  # Conversion de la colonne en array NumPy


der1=3.726510310905925e-06
der2=[]
der2.append(der1)

while (sum(der2)<(pop_rate[-1]-1)):
    
    der2.append(der2[-1]+der1)
    

for i in range(len(der2)-4):
    pop_rate=np.hstack((pop_rate,pop_rate[-1]-der2[-i-1]))

if years_sim>2100:    
    pop_rate = np.pad(pop_rate, (0, l_simu - len(pop_rate)),constant_values=1)

# %% ############## TOWN CREATION #######################################################################################################
scenario_name = ['Engagé', 'Réaliste','Standard']          # same name in excel

path_ren = ["database/221207_TOOL_2032_BillQuantitiesV5_RénoCésar.xlsx",
             "database/221207_TOOL_2032_BillQuantitiesV5_RénoBlonay.xlsx"]

path_new = ["database/221207_TOOL_2032_BillQuantitiesV5_NeufKybourg.xlsx",
        "database/221207_TOOL_2032_BillQuantitiesV5_NeufRiaz.xlsx"]

############### TOWN ACTUAL #######################################################################################################
#####################  import scenario ###############################################################
scenario = Import_scenario(path_ren, scenario_name)
######################  import archetype    ####################################################################################
with open('regbl/town_simpl_regbl.pkl', 'rb') as f:      # from regbl
    arch_regbl = pickle.load(f)

arch_regbl[0][-1].periode2=2024
arch_regbl[1][-1].periode2=2024

bstockinit={'tot':[], # surface de plus de 30 ans qui n'ont pas été rénovée
            'dem':[],     # surface qui sont démolies cette année
            'ren':[],     # surface qui sont rénovée cette année avec le scénario du temps t
            'rendem':[],  # surface qui sont rénovée cette année avec le scénario dans lequelle elle se trouve au temps t
            'new':[],     # surface qui sont construite cette année
            'tran':[],    # surface qui sont transformée cette année
 
            'totcon':[],  # surface construite il y a 30 ans qui subisse une maintenance
            'main':[]}    # surface rénovée il y a 30 ans qui subisse une maintenance


for building in arch_regbl:
    for ar in building:
    
        # calculate the actual surface of each scenario 
        
        surface=np.zeros((l_simu+time_deep+time_dem,3,3), dtype='f')
        if ar.periode2<(yearsbegin):
            for i in range(len(rate_scen_init)):
                surface[0,i,i]=ar.eratot*rate_scen_init[i]
        elif ar.periode1<(yearsbegin):
            ar.erayear=ar.eratot/(ar.periode2-ar.periode1+1)
            for i in range(len(rate_scen_init)):
                surface[0,i,i]=ar.erayear*(yearsbegin-ar.periode1+1)*rate_scen_init[i]            
            for it_time in range(ar.periode2-yearsbegin):
                for i in range(len(rate_scen_init)):
                    surface[1+it_time,i,i]=ar.erayear*rate_scen_init[i]  
        else:      
            ar.erayear=ar.eratot/(ar.periode2-ar.periode1+1)
            for it_time in range(ar.periode2-ar.periode1+1):
                for i in range(len(rate_scen_init)):
                    surface[ar.periode1-yearsbegin+it_time,i,i]=ar.erayear*rate_scen_init[i] 
        
        bstockinit['tot'].append(copy.deepcopy(surface))                                        # set the data from excel
        # add zero to calculate the data        
        bstockinit['dem'].append(np.zeros((l_simu+time_deep+time_dem,3,3), dtype='f'))
        bstockinit['rendem'].append(np.zeros((l_simu+time_deep+time_dem,3,3), dtype='f'))
        bstockinit['ren'].append(np.zeros((l_simu+time_deep+time_dem,3,3), dtype='f'))
        bstockinit['main'].append(np.zeros((l_simu+time_deep+time_dem,3,3), dtype='f'))
        
    bstockinit['tot'].append(np.zeros((l_simu+time_deep+time_dem,3,3), dtype='f'))
    bstockinit['dem'].append(np.zeros((l_simu+time_deep+time_dem,3,3), dtype='f'))
    bstockinit['rendem'].append(np.zeros((l_simu+time_deep+time_dem,3,3), dtype='f'))
    bstockinit['ren'].append(np.zeros((l_simu+time_deep+time_dem,3,3), dtype='f'))
    bstockinit['new'].append(np.zeros((l_simu+time_deep+time_dem,3,3), dtype='f'))
    bstockinit['tran'].append(np.zeros((l_simu+time_deep+time_dem,3,3), dtype='f'))   
    bstockinit['main'].append(np.zeros((l_simu+time_deep+time_dem,3,3), dtype='f'))


########### create building (scenario + archetype) ####################################################################################
archetype = []
for building in arch_regbl:
    for ar in building:
        archetype.append(copy.deepcopy(ar))  # set the data from excel
    archetype.append(copy.deepcopy(ar))

# not a real building but group of building with the same characteristics

########### create town (list of building) ####################################################################################
town_actual = Create_town(scenario, archetype)

########## create scenario for demolition of the actual building #############################################################################
scenario_str = Import_scenario_mix(path_new, scenario_name,60)
scenario_iso = Import_scenario_mix(path_new, scenario_name,30)
scenario_iso2 = Import_scenario_mix(path_ren, scenario_name,30)
town_demo_str = Create_town(scenario_str, archetype)
town_demo_iso = Create_town(scenario_iso, archetype)
town_demo_iso2 = Create_town(scenario_iso2, archetype)
############### TOWN FUTUR ########################################################################################################
######################  archetype from last regbl archetype    ####################################################################################
archetype = []
for building in arch_regbl:
    ar = building[-1]
    archetype.append(copy.deepcopy(ar))  # set the data from excel

scenario = Import_scenario(path_ren, scenario_name)
town_trans = Create_town(scenario, archetype)

#####################  import scenario ###############################################################
# scenario name same as TOWN ACTUAL
scenario = Import_scenario(path_new, scenario_name)
########### create town (list of building (scenario + archetype)) ####################################################################################
# not a real building but group of building with the same characteristics
town_new = Create_town(scenario, archetype)

############  timer ######################################################################################################################### 
end = timer()
print("init time: ", end - start, "seconds")

start = timer()
# %% ############## Outcome init ###########################################################################################################
############# creation/init of the useful data #######
Init_town(town_actual, outcome, outcome_permat, outcome_mat)  # ville actuel
Init_town(town_trans, outcome, outcome_permat, outcome_mat) # ville pour la transformation
Init_town(town_new, outcome, outcome_permat, outcome_mat)   # ville pour les nouvelles constructions
Init_town(town_demo_iso, outcome, outcome_permat, outcome_mat)  # ville pour la démolition de l'isolation de la nouvelle
Init_town(town_demo_iso2, outcome, outcome_permat, outcome_mat) # ville pour la démolition de l'isolation de la réno
Init_town(town_demo_str, outcome, outcome_permat, outcome_mat)#  ville pour la démolition de la structure de la réno
# %% ############## Variable declaration ##############################################################################################

impact_ren = [Init_Impact_Result(outcome, outcome_mat, outcome_permat, l_simu+time_dem) for _ in range(var)]
impact_mai= [Init_Impact_Result(outcome, outcome_mat, outcome_permat, l_simu+time_dem) for _ in range(var)]
impact_new  = [Init_Impact_Result(outcome, outcome_mat, outcome_permat, l_simu+time_dem) for _ in range(var)]
impact_dem = [Init_Impact_Result(outcome, outcome_mat, outcome_permat, l_simu+time_dem) for _ in range(var)]
impact_tot = [Init_Impact_Result(outcome, outcome_mat, outcome_permat, l_simu+time_dem) for _ in range(var)]  
          
bstock_var=[]             
# %% ############## Init state calculation ############################################################################################
surf_init = np.sum(bstockinit['tot'])
m2_init = surf_init/population_init

rate_ren_before=np.linspace(0, rate_ren_init, 31)

## init evolution ##########################################

# just to init surface
surf = {'init': np.linspace(surf_init, surf_init, l_simu),
        'new': np.zeros((l_simu, var), dtype='f'),
        'reno': np.zeros((l_simu, var), dtype='f'),
        'build': np.zeros((l_simu, var), dtype='f'),
        'evol': np.zeros((l_simu, var), dtype='f'),
        'demo': np.zeros((l_simu, var), dtype='f'),
        'main': np.zeros((l_simu, var), dtype='f')
        }
# evolution of the population
population = []
population.append(population_init)
population_new = []

for i in range(l_simu):
    population_new.append(population[-1]*(pop_rate[i]-1))
    population.append(population[-1]*pop_rate[i])

# save the time zero
save_town_init = []
save_town_init.append(copy.deepcopy(town_actual))
save_town_init.append(copy.deepcopy(town_trans))
save_town_init.append(copy.deepcopy(town_new))

save_before_ren(town_actual)
# timer

end = timer()
print("Outcome preparation: ", end - start, "seconds")


# %% ############## Main calculation ############################################################################################################
start = timer()

it_var = -1
for f in combinations:      # for each combination of variable
    it_var += 1
    rate_ren_2050 = f[0]      # renovation rate
    rate_dem_2050 = f[1]      # demolition rate
    rate_scen_end = f[2]      # type scenario
    temp50=f[4]               # year of 50% of the end state

# rate of each scenario from init to end year
    resultat_interpolation = linear_interpolate(rate_scen_init,rate_scen_end,0.5)
    temp_l=np.linspace(rate_scen_init, resultat_interpolation, temp50 - years_init+1)
    rate_scenario=np.concatenate([temp_l[:-1], np.linspace(resultat_interpolation, rate_scen_end, years_stop - temp50), np.linspace(rate_scen_end, rate_scen_end, l_simu - l_inter)])
# surface evolution
    m2_per_hab = np.pad(np.linspace(m2_init, f[3], l_inter), (0, l_simu - l_inter), constant_values=f[3])
    
# renovation rate    
    if years_sim>2100:
        rate_ren= np.pad(np.linspace(rate_ren_init, rate_ren_2050, l_inter), (0, int(45//(rate_ren_2050*100))), 'linear_ramp', end_values= 1/60-rate_dem_2050)
        rate_ren= np.pad(rate_ren, (0, l_simu-len(rate_ren)),constant_values= 1/60-rate_dem_2050)
    else:
        rate_ren= np.pad(np.linspace(rate_ren_init, rate_ren_2050, l_inter), (0, l_simu - l_inter),constant_values= 1/60-rate_dem_2050)

# demolition rate    
    rate_dem= np.pad(np.linspace(rate_dem_init, rate_dem_2050, l_inter), (0, l_simu - l_inter),constant_values= rate_dem_2050)
    
# m2 new due to the new habitant
    surf['new'][:, it_var] = m2_per_hab*population_new
    surf['evol'][:, it_var] = m2_per_hab*population[1:]
    surf['demo'][:, it_var] = rate_dem*surf['evol'][:, it_var]
    surf['reno'][:, it_var] = rate_ren*surf['evol'][:, it_var]
    surf['build'][:, it_var] = surf['new'][:, it_var]+surf['demo'][:, it_var]
    

############ calcul of area and scénarios for each building #################################
    bstock=copy.deepcopy(bstockinit)

    bstockinit['totcon']=copy.deepcopy(bstockinit['tot'])
    for it_stock in bstockinit['totcon']:
        it_stock[:-1] = it_stock[1:]
        it_stock[-1] = 0
        
    bstock['totcon']=copy.deepcopy(bstockinit['totcon'])
        
    for it_time in range(l_simu):
        total_sum = np.sum([np.sum(array[it_time,:,:]) for array in bstock['tot']])
        for it_s in range(len(bstock['tot'])):
#            bstock['totsum'][it_s][it_time,:,:]=sum(bstock['tot'][it_s][it_time:,:,:])
            bstock['dem'][it_s][it_time,:,:]=bstock['tot'][it_s][it_time,:,:]/total_sum*surf['demo'][it_time,it_var]

            bstock['rendem'][it_s][it_time,:,:]=bstock['tot'][it_s][it_time,:,:]/total_sum*surf['reno'][it_time,it_var]
            
            
            if it_time<30:
                bstockinit['main'][it_s][it_time,:,:]=sum(bstockinit['tot'][it_s][:it_time+1,:,:])*rate_ren_before[it_time]
            
            bstock['main'][it_s][it_time,:,:]= bstockinit['main'][it_s][it_time,:,:]
                

            for bstc, tme in zip([bstock['totcon'][it_s],bstock['main'][it_s],bstock['tot'][it_s]],[0,0,time_ren]):# chaque année de maintenance, le stock de cette année se transforme
                temp_sum=rate_scenario[it_time,2]/np.sum(bstc[it_time,:,2])*np.sum(bstc[it_time]) if np.sum(bstc[it_time,:,2]) != 0 else 0   
                temp_sum = max(0, min(1, temp_sum))
                  
                bstc[it_time+tme,:,1]+=bstc[it_time+tme,:,2]*(1-temp_sum)
                bstc[it_time+tme,:,2]=bstc[it_time+tme,:,2]*temp_sum   
            


            bstock['tot'][it_s][it_time+1,:,:]+=bstock['tot'][it_s][it_time,:,:]-bstock['dem'][it_s][it_time,:,:]-bstock['rendem'][it_s][it_time,:,:]
 
            
            for it_scen in range(len(rate_scenario[it_time])):
                bstock['ren'][it_s][it_time,it_scen,:]=np.sum(bstock['rendem'][it_s][it_time,it_scen,:])*rate_scenario[it_time]
                bstock['tot'][it_s][it_time+time_deep,it_scen,:]+=bstock['ren'][it_s][it_time,it_scen,:] #TODO bonne catégorie selon rate_scenario
                
            bstockinit['main'][it_s][it_time+time_ren,:,:]=bstock['ren'][it_s][it_time,:,:]

        #nouvelle construction
        for it_scen in range(len(rate_scenario[it_time])):
            bstock['new'][0][it_time,it_scen,it_scen]=surf['build'][it_time, it_var]*rate_SvsM[0]*(1-rate_tran)*rate_scenario[it_time][it_scen]
            bstock['new'][1][it_time,it_scen,it_scen]=surf['build'][it_time, it_var]*rate_SvsM[1]*(1-rate_tran)*rate_scenario[it_time][it_scen]
            
            bstock['tot'][9][it_time+time_deep,it_scen,it_scen]+=bstock['new'][0][it_time,it_scen,it_scen]
            bstock['tot'][19][it_time+time_deep,it_scen,it_scen]+=bstock['new'][1][it_time,it_scen,it_scen]
            
        #transformation    
            bstock['tran'][0][it_time,it_scen,:]=surf['build'][it_time, it_var]*rate_SvsM[0]*(rate_tran)*rate_scenario[it_time]*rate_scen_init[it_scen]
            bstock['tran'][1][it_time,it_scen,:]=surf['build'][it_time, it_var]*rate_SvsM[1]*(rate_tran)*rate_scenario[it_time]*rate_scen_init[it_scen]
        
            bstock['tot'][9][it_time+time_deep,it_scen,:]+=bstock['tran'][0][it_time,it_scen,:]  
            bstock['tot'][19][it_time+time_deep,it_scen,:]+=bstock['tran'][1][it_time,it_scen,:]    

        bstockinit['totcon'][9][it_time+time_ren,:,:]+=bstock['new'][0][it_time,:,:]+bstock['tran'][0][it_time,:,:]
        bstockinit['totcon'][19][it_time+time_ren,:,:]+=bstock['new'][1][it_time,:,:]+bstock['tran'][1][it_time,:,:]
        bstock['totcon'][9][it_time+time_ren,:,:]+=bstock['new'][0][it_time,:,:]+bstock['tran'][0][it_time,:,:]
        bstock['totcon'][19][it_time+time_ren,:,:]+=bstock['new'][1][it_time,:,:]+bstock['tran'][1][it_time,:,:]     
        
        
    for it_s in range(len(bstock['tot'])):
        rep = np.repeat( bstockinit['totcon'][it_s][0:1, :, :], 10, axis=0)  # (10, 3, 3)
        bstockinit['totcon'][it_s] = np.concatenate((rep, bstockinit['totcon'][it_s]), axis=0)
        rep = np.repeat( bstock['totcon'][it_s][0:1, :, :], 10, axis=0)  # (10, 3, 3)
        bstock['totcon'][it_s] = np.concatenate((rep, bstock['totcon'][it_s]), axis=0)
        
    bstock_var.append(bstock)  


######################## calcul of outcome ##############################################################################################################

## construction new and trans

    for it_scen in range(len(rate_scen_init)):

        phase='construction'
        for it_out in outcome:
            impact_new[it_var].phase[phase].data_time[it_out][:] += np.hstack((time_shift[phase][0],sum(k1[:l_simu,it_scen,it_scen]*k.surface['total'].phase[phase].data[it_out] for k1, k in zip(bstock['new'],town_new[it_scen].bat)), time_shift[phase][1]))
            impact_new[it_var].phase[phase].data_time[it_out][:] += np.hstack((time_shift[phase][0],sum(np.sum(k1[:l_simu,:,it_scen],1)*k.surface['total'].phase[phase].data[it_out] for k1, k in zip(bstock['tran'],town_trans[it_scen].bat)), time_shift[phase][1]))
    
            impact_new[it_var].phase[phase].data[it_out] = sum(impact_new[it_var].phase[phase].data_time[it_out][:l_analyse])
    
        for it_permat in outcome_permat:
            for mat in outcome_mat:
                impact_new[it_var].phase[phase].material[mat].data_time[it_permat] += np.hstack((time_shift[phase][0],sum(k1[:l_simu,it_scen,it_scen]* k.surface['total'].phase[phase].material[mat].data[it_permat] for k1, k in zip(bstock['new'],town_new[it_scen].bat)), time_shift[phase][1]))
                impact_new[it_var].phase[phase].material[mat].data_time[it_permat] += np.hstack((time_shift[phase][0],sum(np.sum(k1[:l_simu,:,it_scen],1)* k.surface['total'].phase[phase].material[mat].data[it_permat] for k1, k in zip(bstock['tran'],town_trans[it_scen].bat)), time_shift[phase][1]))
                
                impact_new[it_var].phase[phase].material[mat].data[it_permat] = sum(impact_new[it_var].phase[phase].material[mat].data_time[it_permat][:l_analyse])


# construction renovation
    for it_scen in range(len(rate_scen_init)):

        phase='construction'
        for it_out in outcome:
            impact_ren[it_var].phase[phase].data_time[it_out][:] += np.hstack((time_shift[phase][0],sum(np.sum(k1[:l_simu,:,it_scen],1)*k.surface['total'].phase[phase].data[it_out] for k1, k in zip(bstock['ren'],town_actual[it_scen].bat)), time_shift[phase][1]))
    
            impact_ren[it_var].phase[phase].data[it_out] = sum(impact_ren[it_var].phase[phase].data_time[it_out][:l_analyse])
    
        for it_permat in outcome_permat:
            for mat in outcome_mat:
                impact_ren[it_var].phase[phase].material[mat].data_time[it_permat] += np.hstack((time_shift[phase][0],sum(np.sum(k1[:l_simu,:,it_scen],1)* k.surface['total'].phase[phase].material[mat].data[it_permat] for k1, k in zip(bstock['ren'],town_actual[it_scen].bat)), time_shift[phase][1]))
                
                impact_ren[it_var].phase[phase].material[mat].data[it_permat] = sum(impact_ren[it_var].phase[phase].material[mat].data_time[it_permat][:l_analyse])
   


## demolion et de la demolion for renovation
    for it_scen in range(len(rate_scen_init)):
        phase='demolition'
        for it_out in outcome:
            impact_dem[it_var].phase[phase].data_time[it_out][:] += np.hstack((time_shift['construction'][0],sum(np.sum(k1[:l_simu,:,it_scen],1)*k.surface['total'].phase[phase].data[it_out] for k1, k in zip(bstock['dem'],town_demo_str[it_scen].bat)), time_shift['construction'][1]))       
            impact_dem[it_var].phase[phase].data_time[it_out][:] += np.hstack((time_shift['construction'][0],sum(np.sum(k1[:l_simu,it_scen,:],1)*k.surface['total'].phase[phase].data[it_out] for k1, k in zip(bstock['dem'],town_demo_iso[it_scen].bat)), time_shift['construction'][1]))       
            
            impact_dem[it_var].phase[phase].data_time[it_out][:] += np.hstack((time_shift['construction'][0],sum(np.sum(k1[:l_simu,it_scen,:],1)*k.surface['total'].phase[phase].data[it_out] for k1, k in zip(bstock['rendem'],town_demo_iso2[it_scen].bat)), time_shift['construction'][1]))       

            impact_dem[it_var].phase[phase].data[it_out] = sum(impact_dem[it_var].phase[phase].data_time[it_out][:l_analyse])
    
        for it_permat in outcome_permat:
            for mat in outcome_mat:
                impact_dem[it_var].phase[phase].material[mat].data_time[it_permat] += np.hstack((time_shift['construction'][0],sum(np.sum(k1[:l_simu,:,it_scen],1)* k.surface['total'].phase[phase].material[mat].data[it_permat] for k1, k in zip(bstock['dem'],town_demo_str[it_scen].bat)), time_shift['construction'][1]))
                impact_dem[it_var].phase[phase].material[mat].data_time[it_permat] += np.hstack((time_shift['construction'][0],sum(np.sum(k1[:l_simu,it_scen,:],1)* k.surface['total'].phase[phase].material[mat].data[it_permat] for k1, k in zip(bstock['dem'],town_demo_iso[it_scen].bat)), time_shift['construction'][1]))

                impact_dem[it_var].phase[phase].material[mat].data_time[it_permat] += np.hstack((time_shift['construction'][0],sum(np.sum(k1[:l_simu,it_scen,:],1)* k.surface['total'].phase[phase].material[mat].data[it_permat] for k1, k in zip(bstock['rendem'],town_demo_iso2[it_scen].bat)), time_shift['construction'][1]))

                impact_dem[it_var].phase[phase].material[mat].data[it_permat] = sum(impact_dem[it_var].phase[phase].material[mat].data_time[it_permat][:l_analyse])
   
# maintenance
    for it_scen in range(len(rate_scen_init)):
        
        # ce qui est démoli de la maintenance est démoli selon l'ancien scénario
        for it_out in outcome:  
            phase='demolition' 
            impact_mai[it_var].phase[phase].data_time[it_out][:] += np.hstack((time_shift['construction'][0],sum(np.sum(k1[10:l_simu+10,it_scen,:],1)*k.surface['total'].phase[phase].data[it_out] for k1, k in zip(bstockinit['totcon'],town_demo_iso[it_scen].bat)), time_shift['construction'][1]))
            impact_mai[it_var].phase[phase].data_time[it_out][:] += np.hstack((time_shift['construction'][0],sum(np.sum(k1[:l_simu,it_scen,:],1)*k.surface['total'].phase[phase].data[it_out] for k1, k in zip(bstockinit['main'],town_demo_iso2[it_scen].bat)), time_shift['construction'][1]))
        
        # ce qui est reconstruit est reconstruit avec le nouveau scenario
            phase='construction'        
            impact_mai[it_var].phase[phase].data_time[it_out][:] += np.hstack((time_shift['construction'][0],sum(np.sum(k1[10:l_simu+10,it_scen,:],1)*k.surface['total'].phase[phase].data[it_out] for k1, k in zip(bstock['totcon'],town_demo_iso[it_scen].bat)), time_shift['construction'][1]))
            impact_mai[it_var].phase[phase].data_time[it_out][:] += np.hstack((time_shift['construction'][0],sum(np.sum(k1[:l_simu,it_scen,:],1)*k.surface['total'].phase[phase].data[it_out] for k1, k in zip(bstock['main'],town_demo_iso2[it_scen].bat)), time_shift['construction'][1]))

        # pour la maintenance 20 et 40 ans, on prend un changement 1:1 avec le nouveau scenario car pour les émissions ça change rien, mais ça nous permet de calculer le bois
            phase='maintenance20'    
            impact_mai[it_var].phase[phase].data_time[it_out][:] += np.hstack((time_shift['construction'][0],sum(np.sum(k1[20:l_simu+10,it_scen,:],1)*k.surface['total'].phase[phase].data[it_out] for k1, k in zip(bstock['totcon'],town_demo_iso[it_scen].bat)), time_shift['maintenance30'][1], time_shift['maintenance20'][1]))
            impact_mai[it_var].phase[phase].data_time[it_out][:] += np.hstack((time_shift['construction'][0],sum(np.sum(k1[10:l_simu,it_scen,:],1)*k.surface['total'].phase[phase].data[it_out] for k1, k in zip(bstock['main'],town_demo_iso2[it_scen].bat)),time_shift['maintenance30'][1], time_shift['maintenance20'][1]))         
            
            phase='maintenance40'                
            impact_mai[it_var].phase[phase].data_time[it_out][:] += np.hstack((time_shift['construction'][0],sum(np.sum(k1[:l_simu+10,it_scen,:],1)*k.surface['total'].phase[phase].data[it_out] for k1, k in zip(bstock['totcon'],town_demo_iso[it_scen].bat)), time_shift['maintenance30'][1], time_shift['maintenance40'][1]))
            impact_mai[it_var].phase[phase].data_time[it_out][:] += np.hstack((time_shift['time10'][0],sum(np.sum(k1[:l_simu,it_scen,:],1)*k.surface['total'].phase[phase].data[it_out] for k1, k in zip(bstock['main'],town_demo_iso2[it_scen].bat)), time_shift['maintenance30'][1], time_shift['maintenance40'][1]))
    
            impact_mai[it_var].phase[phase].data[it_out] = sum(impact_mai[it_var].phase[phase].data_time[it_out][:l_analyse])
                
            
        for it_permat in outcome_permat:     
            for mat in outcome_mat:
                phase='demolition' 
                impact_mai[it_var].phase[phase].material[mat].data_time[it_permat] += np.hstack((time_shift['construction'][0],sum(np.sum(k1[10:l_simu+10,it_scen,:],1)* k.surface['total'].phase[phase].material[mat].data[it_permat] for k1, k in zip(bstockinit['totcon'],town_demo_iso[it_scen].bat)), time_shift['construction'][1]))                    
                impact_mai[it_var].phase[phase].material[mat].data_time[it_permat] += np.hstack((time_shift['construction'][0],sum(np.sum(k1[:l_simu,it_scen,:],1)* k.surface['total'].phase[phase].material[mat].data[it_permat] for k1, k in zip(bstockinit['main'],town_demo_iso2[it_scen].bat)), time_shift['construction'][1]))                    

                phase='construction'     
                impact_mai[it_var].phase[phase].material[mat].data_time[it_permat] += np.hstack((time_shift['construction'][0],sum(np.sum(k1[10:l_simu+10,it_scen,:],1)* k.surface['total'].phase[phase].material[mat].data[it_permat] for k1, k in zip(bstock['totcon'],town_demo_iso[it_scen].bat)), time_shift['construction'][1]))                    
                impact_mai[it_var].phase[phase].material[mat].data_time[it_permat] += np.hstack((time_shift['construction'][0],sum(np.sum(k1[:l_simu,it_scen,:],1)* k.surface['total'].phase[phase].material[mat].data[it_permat] for k1, k in zip(bstock['main'],town_demo_iso2[it_scen].bat)), time_shift['construction'][1]))                    

                phase='maintenance20'     
                impact_mai[it_var].phase[phase].material[mat].data_time[it_permat] += np.hstack((time_shift['construction'][0],sum(np.sum(k1[20:l_simu+10,it_scen,:],1)* k.surface['total'].phase[phase].material[mat].data[it_permat] for k1, k in zip(bstock['totcon'],town_demo_iso[it_scen].bat)), time_shift['maintenance30'][1], time_shift['maintenance20'][1]))                    
                impact_mai[it_var].phase[phase].material[mat].data_time[it_permat] += np.hstack((time_shift['construction'][0],sum(np.sum(k1[10:l_simu,it_scen,:],1)* k.surface['total'].phase[phase].material[mat].data[it_permat] for k1, k in zip(bstock['main'],town_demo_iso2[it_scen].bat)), time_shift['maintenance30'][1], time_shift['maintenance20'][1]))                    

                phase='maintenance40'     
                impact_mai[it_var].phase[phase].material[mat].data_time[it_permat] += np.hstack((time_shift['construction'][0],sum(np.sum(k1[:l_simu+10,it_scen,:],1)* k.surface['total'].phase[phase].material[mat].data[it_permat] for k1, k in zip(bstock['totcon'],town_demo_iso[it_scen].bat)), time_shift['maintenance30'][1], time_shift['maintenance40'][1]))                    
                impact_mai[it_var].phase[phase].material[mat].data_time[it_permat] += np.hstack((time_shift['time10'][0],sum(np.sum(k1[:l_simu,it_scen,:],1)* k.surface['total'].phase[phase].material[mat].data[it_permat] for k1, k in zip(bstock['main'],town_demo_iso2[it_scen].bat)), time_shift['maintenance30'][1], time_shift['maintenance40'][1]))                    


                impact_mai[it_var].phase[phase].material[mat].data[it_permat] = sum(impact_mai[it_var].phase[phase].material[mat].data_time[it_permat][:l_analyse])

########################## compute the data together #####################################################################################################################
    for it_out in outcome:
        impact_ren[it_var].calcul_data(it_out)
        impact_new[it_var].calcul_data(it_out)
        impact_dem[it_var].calcul_data(it_out)
        impact_mai[it_var].calcul_data(it_out)
        
        impact_ren[it_var].data_time[it_out] = impact_ren[it_var].phase['construction'].data_time[it_out]
        impact_new[it_var].data_time[it_out]  =  impact_new[it_var].phase['construction'].data_time[it_out]
        impact_dem[it_var].data_time[it_out] = impact_dem[it_var].phase['demolition'].data_time[it_out]
        impact_mai[it_var].data_time[it_out] = sum(sphase.data_time[it_out] for sphase in impact_mai[it_var].phase.values())
        
    for it_permat in outcome_permat:
        for mat in outcome_mat:
            impact_ren[it_var].material[mat].data_time[it_permat] = sum(sphase.material[mat].data_time[it_permat] for sphase in impact_ren[it_var].phase.values())
            impact_new[it_var].material[mat].data_time[it_permat]  = sum(sphase.material[mat].data_time[it_permat] for sphase in impact_new[it_var].phase.values())
            impact_dem[it_var].material[mat].data_time[it_permat] = sum(sphase.material[mat].data_time[it_permat] for sphase in impact_dem[it_var].phase.values())
            impact_mai[it_var].material[mat].data_time[it_permat] = sum(sphase.material[mat].data_time[it_permat] for sphase in impact_mai[it_var].phase.values())        

# gwp dynamic
    impact_ren[it_var].data_time['gwp2050'] = impact_ren[it_var].data_time['gwp2050']*rate_time+impact_ren[it_var].data_time['gwp']*(1-rate_time)
    impact_new[it_var].data_time['gwp2050']  = impact_new[it_var].data_time['gwp2050']*rate_time+impact_new[it_var].data_time['gwp']*(1-rate_time)
    impact_dem[it_var].data_time['gwp2050'] = impact_dem[it_var].data_time['gwp2050']*rate_time+impact_dem[it_var].data_time['gwp']*(1-rate_time)
    impact_mai[it_var].data_time['gwp2050'] = impact_mai[it_var].data_time['gwp2050']*rate_time+impact_mai[it_var].data_time['gwp']*(1-rate_time)

# compute the total
    impact_tot[it_var]=impact_ren[it_var]+impact_new[it_var]+impact_dem[it_var]+impact_mai[it_var]
 
    
#################### timer ####################################################
end = timer()
print("Main calcul: ", end - start, "seconds")

# %% ############## RESULT ########################
start = timer()
    
res_gwp_new = np.zeros(var, dtype=float)
res_bio_new = np.zeros(var, dtype=float)
res_gwp_ren = np.zeros(var, dtype=float)
res_bio_ren = np.zeros(var, dtype=float)
res_gwp_dem = np.zeros(var, dtype=float)
res_bio_dem = np.zeros(var, dtype=float)
res_gwp_mai = np.zeros(var, dtype=float)
res_bio_mai = np.zeros(var, dtype=float)

for it in range(len(impact_new)):
    res_gwp_new[it] = impact_new[it].data['gwp2050']/1e9
    res_bio_new[it] = impact_new[it].phase['construction'].data['bio']/1e9

    res_gwp_ren[it] = impact_ren[it].data['gwp2050']/1e9
    res_bio_ren[it] = impact_ren[it].phase['construction'].data['bio']/1e9
    
    res_gwp_dem[it] = impact_dem[it].data['gwp2050']/1e9
    res_bio_dem[it] = impact_dem[it].phase['construction'].data['bio']/1e9

    res_gwp_mai[it] = impact_mai[it].data['gwp2050']/1e9
    res_bio_mai[it] = impact_mai[it].data['bio']/1e9
    
res_cumul_new = res_gwp_new+res_bio_new
res_cumul_ren = res_gwp_ren+res_bio_ren
res_gwp = res_gwp_new+res_gwp_ren+res_gwp_dem+res_gwp_mai
res_bio = res_bio_new+res_bio_ren+res_bio_mai
# %% Graph data supplementaire

df_var = pd.DataFrame({variable_name[0]: [f[0] for f in combinations_data],
                       variable_name[1]: [f[1] for f in combinations_data],
                       variable_name[2]: [f[2] for f in combinations_data],
                       variable_name[3]: [f[3] for f in combinations_data],
                       variable_name[4]: [f[4] for f in combinations_data],
                       })

df_var2=pd.DataFrame({variable_name[0]: [f[0] for f in combinations_data],
                       variable_name[1]: [f[1] for f in combinations_data],
                       variable_name[2]: [f[2] for f in combinations_data],
                       variable_name[3]: [f[3] for f in combinations_data],
                       variable_name[4]: [f[4] for f in combinations_data],
                       'New area <br> (Mm2)': sum(surf['new'][:l_2050])/1e6, 
                        'New build area <br> (Mm2)':sum(surf['build'][:l_2050])/1e6,
                       'Reno areas <br> (Mm2) <br>': sum(surf['reno'][:l_2050])/1e6,
                        'Embodied new <br> (MtCO2)':res_gwp_new,
                        'Bio content new <br> (MtCO2)':-res_bio_new,
                        'Embodied ren <br> (MtCO2)':res_gwp_ren,
                        'Bio content ren <br> (MtCO2)':-res_bio_ren,
                        'Embodied dem <br> (MtCO2)':res_gwp_dem,
                        'Embodied mai <br> (MtCO2)':res_gwp_mai,
                        'Embodied total <br> (MtCO2)':res_gwp,
                        'Bio content total <br> (MtCO2)':-(res_bio_ren+res_bio_new)
                       })



filtered_data = df_var[(df_var['m2 per hab'] == var_rate_m2_per_hab[1]) & (df_var['Renovation rate'] == var_rate_ren[0]) & (df_var['Demolition rate'] == var_rate_dem[0]) & (df_var['Scenario'] == 0)  & (df_var['Year 50%']==var_temps50[0])]
ind = filtered_data.index

style=[]
for it in range(len(combinations)):
    if (combinations[it][2]==var_rate_scenario[0]).all():
        style.append('solid')
    if (combinations[it][2]==var_rate_scenario[1]).all():
        style.append('dashdot')
    if (combinations[it][2]==var_rate_scenario[2]).all():
        style.append('dashed')
        
        
style_default=['solid']
marker_bio=["","x","."]
marker_default=[""]

#%%  ############## PARALLEL COORDINATE ########################
# # megatonne de CO2
# # PJ
gr.parallel_coordinate(combinations_data,combinations_name, variable_name, [surf['new'][:l_2050]/1e6, surf['build'][:l_2050]/1e6, surf['reno'][:l_2050]/1e6,res_gwp_new,-res_bio_new,res_gwp_ren,-res_bio_ren,res_gwp_dem,res_gwp_mai,res_gwp,-(res_bio_ren+res_bio_new)],
                                                      ['New area <br> (Mm2)','New build area <br> (Mm2)','Reno areas <br> (Mm2) <br>','Embodied new <br> (MtCO2)','Bio content new <br> (MtCO2)','Embodied ren <br> (MtCO2)','Bio content ren <br> (MtCO2)','Embodied dem <br> (MtCO2)','Embodied mai <br> (MtCO2)','Embodied total <br> (MtCO2)','Bio content total <br> (MtCO2)'],res_gwp)


#%%
##Chose a combination to analyse
filtered_data = df_var[(df_var['m2 per hab'] == var_rate_m2_per_hab[1]) & (df_var['Renovation rate'] == var_rate_ren[1]) & (df_var['Demolition rate'] == var_rate_dem[0]) & (df_var['Scenario'] == 0)  & (df_var['Year 50%']==var_temps50[1])]
ind=filtered_data.index
subtitle=f' m2/hab:{filtered_data.at[ind[0], "m2 per hab"]:.1f},'f' Ren:{filtered_data.at[ind[0], "Renovation rate"]*100:.0f}%,'f' Dem:{filtered_data.at[ind[0], "Demolition rate"]*1000:.0f}‰'

#####
## population  evolution:
population_2050= [p * 1e-6 for p in population[:]]
population_new_2050= [p * 1e-6 for p in population_new[:]]
gr.evolution2(years_init,[population_2050],[population_new_2050],['total','new'],['Population (Millions)','New people per year (Millions)'],'Swiss Population Evolution','',['solid','dashed'],marker_default,years_analyse)

#surface evolution
gr.evolution(years_init,[surf['reno'][:,ind]/1e6,surf['build'][:,ind]/1e6,surf['demo'][:,ind]/1e6],['Renovation Areas','New Constructed Areas','Demolished Areas'],'m2 (Millions)','Evolution of area',subtitle,['solid','dashed','dashdot',':'],marker_default,years_analyse)
gr.cumul(years_init,[surf['reno'][:,ind]/1e6,surf['build'][:,ind]/1e6,surf['demo'][:,ind]/1e6],['Renovation Areas','New Constructed Areas','Demolished Areas'],'m2 (Millions)','Evolution of area',subtitle,['solid','dashed','dashdot',':'],marker_default,years_analyse)

filtered_data1 = df_var[(df_var['m2 per hab'] == var_rate_m2_per_hab[1]) & (df_var['Demolition rate'] == var_rate_dem[2]) & (df_var['Scenario'] == 0)  & (df_var['Year 50%']==var_temps50[1])]
ind1=filtered_data1.index

subtitle=f' m2/hab:{filtered_data.at[ind[0], "m2 per hab"]:.1f},'f' Dem:{filtered_data.at[ind[0], "Demolition rate"]*1000:.0f}‰'

temp=[]
temp.append(surf['build'][:,ind]/1e6)
for it_var in ind1:
    temp.append(surf['reno'][:,it_var]/1e6)


gr.evolution(years_init,temp,['New Constructed Areas','Renovation Areas 1%','Renovation Areas 3%','Renovation Areas 5%'],'m2 (Millions)','Evolution of area',subtitle,['solid','dashed','dashdot',':'],marker_default,years_analyse)


filtered_data1 = df_var[(df_var['m2 per hab'] == var_rate_m2_per_hab[1]) & (df_var['Renovation rate'] == var_rate_ren[1]) & (df_var['Scenario'] == 0)  & (df_var['Year 50%']==var_temps50[1])]
ind1=filtered_data1.index

subtitle=f' m2/hab:{filtered_data.at[ind[0], "m2 per hab"]:.1f}‰'

temp=[]
temp.append(surf['build'][:,ind1]/1e6)
for it_var in ind1:
    temp.append(surf['demo'][:,it_var]/1e6)
    
gr.evolution(years_init,temp,['New 1‰','New 3‰','New 5‰','Demo 1‰','Demo 3‰','Demo 5‰'],'m2 (Millions)','Evolution of area',subtitle,['solid','-.','-.','-.','-.','-.','-.','-.','-.','-.'],[""],years_analyse)


#%%  ############## Embodied carbon ########################


filtered_data = df_var[(df_var['m2 per hab'] == var_rate_m2_per_hab[1]) & (df_var['Renovation rate'] == var_rate_ren[1]) & (df_var['Demolition rate'] == var_rate_dem[0]) & (df_var['Scenario'] == 0)   & (df_var['Year 50%']==var_temps50[1])]
ind=filtered_data.index
subtitle=f' m2/hab:{filtered_data.at[ind[0], "m2 per hab"]:.1f},'f' Ren:{filtered_data.at[ind[0], "Renovation rate"]*100:.0f}%,'f' Dem:{filtered_data.at[ind[0], "Demolition rate"]*1000:.0f}‰,'f' Scen:{var_scenario_name[filtered_data.at[ind[0], "Scenario"]]},'f' Year50%:{filtered_data.at[ind[0], "Year 50%"]}'

# Embodied carbon new
# temp=[]
# for it_var in ind:
#     temp.append(impact_new[it_var].data_time['gwp2050']/1e9)
# gr.evolution(years_init,temp,['embodied carbon'],'MtCO2','Evolution des embodied carbone pour le surface future',subtitle,[style[i] for i in ind],marker_default,years_analyse)
# gr.cumul(years_init,temp,['embodied carbon'],'MtCO2','Evolution des embodied carbone pour le surface future',subtitle,[style[i] for i in ind],marker_default,years_analyse)

# embodied carbon and bio new
temp=[]
tempstyle=[]
#marker=["","+","."]
for it_var in ind:
    temp.append(impact_new[it_var].data_time['gwp2050']/1e9)
    tempstyle.append(style[it_var])
    temp.append(impact_new[it_var].data_time['bio']/1e9)
    tempstyle.append(style[it_var])
    temp.append(impact_new[it_var].data_time['bio0']/1e9)
    tempstyle.append(style[it_var])
#gr.evolution_neg(years_init,temp,['embodied carbon','biogenic (-1/+1)','biogenic (-1/+0)'],'MtCO2','Evolution of Embodied Carbon and biogenic of New Constructed Areas',subtitle,style_default,marker_default,years_analyse)
gr.cumul(years_init,temp,['embodied carbon','biogenic (-1/+1)','biogenic (-1/+0)'],'MtCO2','Cumul of Embodied Carbon and Biogenic of New Constructed Areas',subtitle,['-','-','-.'],marker_default,years_analyse)

temp=[]
for it_var in ind:
    temp.append(impact_new[it_var].data_time['gwp2050']/1e9)
    temp.append(impact_new[it_var].data_time['bio']/1e9)
gr.bar_cumul_neg(years_init,temp,['embodied carbon','biogenic (-1/+1)','biogenic (-1/+0)'],'MtCO2','Evolution of Embodied Carbon and biogenic of New Constructed Areas',subtitle,style_default,marker_default,years_analyse)



# embodied carbon and bio reno
temp=[]
tempstyle=[]
#marker=["","+","."]
for it_var in ind:
    temp.append(impact_ren[it_var].data_time['gwp2050']/1e9)
    temp.append(impact_ren[it_var].data_time['bio']/1e9)
    temp.append(impact_ren[it_var].data_time['bio0']/1e9)
#gr.evolution_neg(years_init,temp,['embodied carbon','biogenic (-1/+1)','biogenic (-1/+0)'],'MtCO2','Evolution of Embodied Carbon and biogenic of New Constructed Areas',subtitle,style_default,marker_default,years_analyse)
gr.cumul(years_init,temp,['embodied carbon','biogenic (-1/+1)','biogenic (-1/+0)'],'MtCO2','Cumul of Embodied Carbon and Biogenic of Renovated Areas',subtitle,['-','-','-.'],marker_default,years_analyse)

temp=[]
for it_var in ind:
    temp.append(impact_ren[it_var].data_time['gwp2050']/1e9)
    temp.append(impact_ren[it_var].data_time['bio']/1e9)
gr.bar_cumul_neg(years_init,temp,['embodied carbon','biogenic (-1/+1)','biogenic (-1/+0)'],'MtCO2','Evolution of Embodied Carbon and biogenic of Renovated Areas',subtitle,style_default,marker_default,years_analyse)



# embodied carbon and bio total
temp=[]
tempstyle=[]
#marker=["","+","."]
for it_var in ind:
    temp.append(impact_tot[it_var].data_time['gwp2050']/1e9)
    temp.append(impact_tot[it_var].data_time['bio']/1e9)
    temp.append(impact_tot[it_var].data_time['bio0']/1e9)
#gr.evolution_neg(years_init,temp,['embodied carbon','biogenic (-1/+1)','biogenic (-1/+0)'],'MtCO2','Evolution of Embodied Carbon and biogenic of New Constructed Areas',subtitle,style_default,marker_default,years_analyse)
gr.cumul(years_init,temp,['embodied carbon','biogenic (-1/+1)','biogenic (-1/+0)'],'MtCO2','Cumul of Embodied Carbon and Biogenic',subtitle,['-','-','-.'],marker_default,years_analyse)

temp=[]
for it_var in ind:
    temp.append(impact_tot[it_var].data_time['gwp2050']/1e9)
    temp.append(impact_tot[it_var].data_time['bio']/1e9)
gr.bar_cumul_neg(years_init,temp,['embodied carbon','biogenic (-1/+1)','biogenic (-1/+0)'],'MtCO2','Evolution of Embodied Carbon and Biogenic',subtitle,style_default,marker_default,years_analyse)



# Embodied carbon both
temp=[]
for it_var in ind:
    temp.append(impact_new[it_var].data_time['gwp2050']/1e9)
    temp.append(impact_ren[it_var].data_time['gwp2050']/1e9)
    temp.append(impact_dem[it_var].data_time['gwp2050']/1e9)
    temp.append(impact_mai[it_var].data_time['gwp2050']/1e9)
gr.evolution(years_init,temp,['New Constructed Areas','Renovated Areas','Demolished Areas','Remplacement Areas'],'MtCO2','Evolution of Embodied Carbon',subtitle,style_default,marker_default,years_analyse)
gr.cumul(years_init,temp,['New Constructed Areas','Renovated Areas','Demolished Areas','Remplacement Areas'],'MtCO2','Cumul of Embodied Carbon',subtitle,style_default,["","","+","."],years_analyse)
gr.bar_cumul(years_init,temp,['New Constructed Areas','Renovated Areas','Demolished Areas','Remplacement Areas'],'MtCO2','Evolution of Embodied Carbon',subtitle,style_default,marker_default,years_analyse)



# why not

temp=[]
for it_var in ind:
    temp.append(impact_tot[it_var].data_time['gwp']/1e9)
    temp.append(impact_tot[it_var].data_time['gwp2050']/1e9)
    temp.append(impact_tot[it_var].data_time['bio']/1e9)
    temp.append(impact_tot[it_var].data_time['bio0']/1e9)
gr.evolution_neg(years_init,temp,['embodied carbon','dyn embodied carbon','biogenic (-1/+1)','biogenic (-1/+0)'],'MtCO2','Evolution of Embodied Carbon and Biogenic',subtitle,style_default,marker_default,years_analyse)
gr.cumul(years_init,temp,['embodied carbon','dyn embodied carbon','biogenic (-1/+1)','biogenic (-1/+0)'],'MtCO2','Cumul of Embodied Carbon and Biogenic',subtitle,style_default,marker_default,years_analyse)



#%%  ############## MATERIAU ########################
for i in [1]:
    filtered_data = df_var[(df_var['m2 per hab'] == var_rate_m2_per_hab[1]) & (df_var['Renovation rate'] == var_rate_ren[2]) & (df_var['Demolition rate'] == var_rate_dem[0])  & (df_var['Year 50%']==var_temps50[i])]
    ind=filtered_data.index
    subtitle=f' m2/hab:{filtered_data.at[ind[0], "m2 per hab"]:.1f},'f' Ren:{filtered_data.at[ind[0], "Renovation rate"]*100:.0f}%,'f' Dem:{filtered_data.at[ind[0], "Demolition rate"]*1000:.0f}‰,'f' Year50%:{filtered_data.at[ind[0], "Year 50%"]}'
    
    # temp=[]
    # for it_var in ind:
    #     temp.append(impact_ren[it_var].material['timber'].data_time['kg']/1e9)
    # gr.evolution(years_init,temp,['Optimistic','Medium','BAU'],'Mt','Evolution of Use of Timber for Renovated Areas',subtitle,[style[i] for i in ind],marker_default,years_analyse)
    # gr.cumul(years_init,temp,['Optimistic','Medium','BAU'],'Mt','Cumul of Use of Timber for Renovated Areas',subtitle,[style[i] for i in ind],marker_default,years_analyse)


    # temp=[]
    # for it_var in ind:
    #     temp.append(impact_ren[it_var].material['vegetal_fiber'].data_time['kg']/1e9)
    # gr.evolution(years_init,temp,['Optimistic','Medium','BAU'],'Mt','Evolution of Use of Biosourced Insulation for Renovated Areas',subtitle,[style[i] for i in ind],marker_default,years_analyse)
    # gr.cumul(years_init,temp,['Optimistic','Medium','BAU'],'Mt','Cumul of Use of Biosourced Insulation for Renovated Areas',subtitle,[style[i] for i in ind],marker_default,years_analyse)
    
    # temp=[]
    # for it_var in ind:
    #     temp.append(impact_new[it_var].material['timber'].data_time['kg']/1e9)
    # gr.evolution(years_init,temp,['Optimistic','Medium','BAU'],'Mt','Evolution of Use of Timber for New Constructed Areas ',subtitle,[style[i] for i in ind],marker_default,years_analyse)
    # gr.cumul(years_init,temp,['Optimistic','Medium','BAU'],'Mt','Cumul of Use of Timber for New Areas',subtitle,[style[i] for i in ind],marker_default,years_analyse)
    
    # temp=[]
    # for it_var in ind:
    #     temp.append(impact_new[it_var].material['vegetal_fiber'].data_time['kg']/1e9)
    # gr.evolution(years_init,temp,['Optimistic','Medium','BAU'],'Mt','Evolution of Use of Biosourced Insulation for New Constructed Areas ',subtitle,[style[i] for i in ind],marker_default,years_analyse)
    # gr.cumul(years_init,temp,['Optimistic','Medium','BAU'],'Mt','Cumul of Use of Biosourced Insulation for New Areas',subtitle,[style[i] for i in ind],marker_default,years_analyse)
    
    temp=[]
    for it_var in ind:
        temp.append(impact_tot[it_var].material['timber'].data_time['kg']/1e9)
    gr.evolution(years_init,temp,['Optimistic','Medium','BAU'],'Mt','Evolution of Use of Timber',subtitle,[style[i] for i in ind],marker_default,years_analyse)
    gr.cumul(years_init,temp,['Optimistic','Medium','BAU'],'Mt','Cumul of Use of Timber',subtitle,[style[i] for i in ind],marker_default,years_analyse)
    gr.bar_cumul_neg(years_init,temp,['Optimistic','Medium','BAU'],'MtCO2','Evolution of Use of Timber',subtitle,style_default,marker_default,years_analyse)
    
    temp=[]
    for it_var in ind:
        temp.append(impact_tot[it_var].material['vegetal_fiber'].data_time['kg']/1e9)
    gr.evolution(years_init,temp,['Optimistic','Medium','BAU'],'Mt','Evolution of Use of Biosourced Insulation',subtitle,[style[i] for i in ind],marker_default,years_analyse)
    gr.cumul(years_init,temp,['Optimistic','Medium','BAU'],'Mt','Cumul of Use of Biosourced Insulation',subtitle,[style[i] for i in ind],marker_default,years_analyse)
    gr.bar_cumul_neg(years_init,temp,['Optimistic','Medium','BAU'],'MtCO2','Evolution of Use of Biosourced Insulation',subtitle,style_default,marker_default,years_analyse)
    

filtered_data = df_var[(df_var['m2 per hab'] == var_rate_m2_per_hab[1]) & (df_var['Renovation rate'] == var_rate_ren[2]) & (df_var['Demolition rate'] == var_rate_dem[2]) & (df_var['Scenario'] == 0) ]
ind=filtered_data.index
subtitle=f' m2/hab:{filtered_data.at[ind[0], "m2 per hab"]:.1f},'f' Ren:{filtered_data.at[ind[0], "Renovation rate"]*100:.0f}%,'f' Dem:{filtered_data.at[ind[0], "Demolition rate"]*1000:.0f}‰,'f' Scen:{var_scenario_name[filtered_data.at[ind[0], "Scenario"]]}'


temp=[]
for it_var in ind:
    temp.append(impact_tot[it_var].material['timber'].data_time['kg']/1e9)
gr.evolution(years_init,temp,['2030','2035','2040','2045'],'Mt','Evolution of Use of Timber',subtitle,[style[i] for i in ind],marker_default,years_analyse)
gr.cumul(years_init,temp,['2030','2035','2040','2045'],'Mt','Cumul of Use of Timber',subtitle,[style[i] for i in ind],marker_default,years_analyse)

#%%  ############## COMPARAISON DEMOLITION ########################

#comparaison de différente valeur de demolition:
filtered_data = df_var[(df_var['m2 per hab'] == var_rate_m2_per_hab[1]) & (df_var['Renovation rate'] == var_rate_ren[1]) & (df_var['Scenario'] == 0)  & (df_var['Year 50%']==var_temps50[0])]
ind=filtered_data.index
subtitle=f' m2/hab:{filtered_data.at[ind[0], "m2 per hab"]:.1f}'

name=[]
temp=[]
for it_var in ind:
    name.append(combinations_data[it_var][1])
    temp.append(surf['demo'][:,it_var]/1e6)

gr.cumul(years_init,temp,name,'m2 (millions)','Evolution of Demolished Areas at Different Demolition Rates',subtitle,[style[i] for i in ind],marker_default,years_sim)
#gr.evolution(years_init,[surf['build'][:,ind]/1e6],name,'m2 (millions)','Evolution of New Constructed Areas at Different Demolition Rates',subtitle,[style[i] for i in ind],marker_default)

temp=[]
for it_var in ind:
    temp.append(surf['build'][:,it_var]/1e6)
gr.cumul(years_init,temp,name,'m2 (millions)','Cumul of New Constructed Areas at Different Demolition Rate',subtitle,[style[i] for i in ind],marker_default,years_sim)

#%%  ############## COMPARAISON RENOVATION ########################
filtered_data = df_var[(df_var['m2 per hab'] == var_rate_m2_per_hab[1]) & (df_var['Demolition rate'] == var_rate_dem[0]) & (df_var['Scenario'] == 1)  & (df_var['Year 50%']==var_temps50[0])]
ind=filtered_data.index
subtitle=f' m2/hab:{filtered_data.at[ind[0], "m2 per hab"]:.1f},'f' Dem:{filtered_data.at[ind[0], "Demolition rate"]*1000:.0f}%'

name=[]
for it_var in ind:
    name.append(combinations_data[it_var][0])
    

#gr.evolution(years_init,[surf['reno'][:,ind]/1e6],name,'m2 (millions)','Evolution of Renovation Areas at Different Renovation Rates',subtitle,[style[i] for i in ind],marker_default)
temp=[]
for it_var in ind:
    temp.append(surf['reno'][:,it_var]/1e6)
gr.cumul(years_init,temp,name,'m2 (millions)','Cumul of Renovation Areas at Different Renovation Rates',subtitle,[style[i] for i in ind],marker_default,years_sim)

#%%  ############## COMPARAISON m2 per person: ########################
## comparaison de différente valeur de m2 per person:
filtered_data = df_var[(df_var['Renovation rate'] == var_rate_ren[2]) & (df_var['Demolition rate'] == var_rate_dem[2]) & (df_var['Scenario'] == 0)   & (df_var['Year 50%']==var_temps50[0])]
ind=filtered_data.index
subtitle=f' Ren:{filtered_data.at[ind[0], "Renovation rate"]*100:.0f}%,'f' Dem:{filtered_data.at[ind[0], "Demolition rate"]*1000:.0f}‰'

name=[]
for it_var in ind:
    name.append(combinations_data[it_var][3])
temp=[]
for it_var in ind:
    temp.append(surf['new'][:,it_var]/1e6)
gr.cumul(years_init,temp,name,'m2 (millions)','Cumul of new Area for Different m² per Person',subtitle,[style[i] for i in ind],marker_default,years_sim)

#%%  ############## COMPARAISON scénarios ########################
# # comparaison entre les scénarios
filtered_data = df_var[(df_var['m2 per hab'] == var_rate_m2_per_hab[1]) & (df_var['Renovation rate'] == var_rate_ren[2]) & (df_var['Demolition rate'] == var_rate_dem[0])  & (df_var['Year 50%']==var_temps50[1])]
ind = filtered_data.index
subtitle=f' m2/hab:{filtered_data.at[ind[0], "m2 per hab"]:.1f},'f' Ren:{filtered_data.at[ind[0], "Renovation rate"]*100:.0f}%,'f' Dem:{filtered_data.at[ind[0], "Demolition rate"]*1000:.0f}‰,'f' Year50%:{filtered_data.at[ind[0], "Year 50%"]}'

# # # Embodied carbon
bstock['tot'][it_s][it_time+1,:,:]
temp = []
for it_var in ind:
    temp.append(impact_new[it_var].data_time['gwp2050']/1e9)
#gr.evolution(years_init, temp, ['Optimistic','Medium','BAU'], 'MtCO2','Evolution of Embodied Carbon of New Constructed Areas',subtitle,[style[i] for i in ind],marker_default, years_analyse)

gr.cumul(years_init, temp, ['Optimistic','Medium','BAU'], 'MtCO2',
          'Cumul of Embodied Carbon of New Constructed Areas',subtitle,[style[i] for i in ind],marker_default, years_sim)


temp = []
for it_var in ind:
    temp.append(impact_ren[it_var].data_time['gwp2050']/1e9)
#gr.evolution(years_init, temp, ['Optimistic','Medium','BAU'], 'MtCO2','Evolution of Embodied Carbon of Renovated Areas',subtitle,[style[i] for i in ind],marker_default, years_analyse)
gr.cumul(years_init, temp, ['Optimistic','Medium','BAU'], 'MtCO2',
          'Cumul of Embodied Carbon of Renovated Areas',subtitle,[style[i] for i in ind],marker_default, years_sim)



temp = []
for it_var in ind:
    temp.append(impact_tot[it_var].data_time['gwp2050']/1e9)
gr.evolution(years_init, temp, ['Optimistic','Medium','BAU'], 'MtCO2','Evolution of Embodied Carbon of New Constructed Areas and Renovated Areas',subtitle,[style[i] for i in ind],marker_default, years_analyse)
gr.cumul(years_init, temp, ['Optimistic','Medium','BAU'], 'MtCO2','Cumul of Embodied Carbon',subtitle,['-','--','-'],marker_default, years_analyse)

#%%  ############## Surface archetype evolution ########################

# TODO à refaire!
# filtered_data = df_var[(df_var['m2 per hab'] == var_rate_m2_per_hab[1]) & (df_var['Renovation rate'] == var_rate_ren[2]) & (df_var['Demolition rate'] == var_rate_dem[0]) & (df_var['Scenario'] == 1)   & (df_var['Year 50%']==var_temps50[0])]
# ind = filtered_data.index
# subtitle=f' m2/hab:{filtered_data.at[ind[0], "m2 per hab"]:.1f},'f' Ren:{filtered_data.at[ind[0], "Renovation rate"]*100:.0f}%,'f' Dem:{filtered_data.at[ind[0], "Demolition rate"]*1000:.0f}‰,'f' Scen:{var_scenario_name[filtered_data.at[ind[0], "Scenario"]]},'f' Year50%:{filtered_data.at[ind[0], "Year 50%"]}'

# #tempsa=np.sum(bstock_var[0]['tot'][archetype][time,sume,sume],axis=(0,1)

# temp = []
# midpoint=len(bstock_var[0]['tot'])//2
# for it_bat in range(midpoint-1):
    
#     temp.append(np.sum(bstock_var[ind[0]]['totsum'][it_bat][:l_2050,:,:],axis=(1,2))+np.sum(bstock_var[ind[0]]['totsum'][it_bat+midpoint][:l_2050,:,:],axis=(1,2)))



# gr.evolution(years_init, temp, ['Before 1919','1919-1945','1946–1960','1961–1970','1971–1980','1981–1990','1991–2000','2001–2010','2011–2024','after 2024','transformation'], 'm2',
#               'Evolution of the Areas',subtitle,[style[i] for i in ind],marker_default)

# a=sum(temp)
# temp1 = []
# temp1.append(a)

# cumulnew=np.cumsum(np.sum(bstock_var[ind[0]]['totsum'][it_bat][:l_2050,:,:],axis=(1,2))+np.sum(bstock_var[ind[0]]['totsum'][it_bat+midpoint][:l_2050,:,:],axis=(1,2)))
# temp.append(cumulnew)
# temp1.append(cumulnew)

# gr.bar_cumul(years_init, temp1, ['old','new'], 'm2','Evolution of the Areas',subtitle,style_default,marker_default)




end = timer()
print("Graph: ", end - start, "seconds")

# %%
filtered_data = df_var[(df_var['m2 per hab'] == var_rate_m2_per_hab[1]) & (df_var['Renovation rate'] == var_rate_ren[0]) & (df_var['Demolition rate'] == var_rate_dem[0])   & (df_var['Year 50%']==var_temps50[0])]
ind = filtered_data.index

print("New GWP_embodied ", impact_new[ind[0]].data['gwp2050']/1e9,impact_new[ind[1]].data['gwp2050']/1e9,impact_new[ind[2]].data['gwp2050']/1e9)
print("Reno GWP_embodied ", impact_ren[ind[0]].data['gwp2050']/1e9,impact_ren[ind[1]].data['gwp2050']/1e9,impact_ren[ind[2]].data['gwp2050']/1e9)
print("Demo GWP_embodied ", impact_dem[ind[0]].data['gwp2050']/1e9,impact_dem[ind[1]].data['gwp2050']/1e9,impact_dem[ind[2]].data['gwp2050']/1e9)
#print("Surface actual construction: ", town_actual[1].bat[0].surftotal[26,ind])
#print("Surface ren: ", town_actual[1].bat[0].surf[26,ind])
#print("Surface dem: ", town_actual[1].bat[0].surfdem[26,ind])


# %%
# filtered_data = df_var[(df_var['m2 per hab'] == var_rate_m2_per_hab[1]) & (df_var['Renovation rate'] == var_rate_ren[2]) & (df_var['Demolition rate'] == var_rate_dem[0])   & (df_var['Scenario']== 0)]
# ind = filtered_data.index

# print("New GWP_embodied ", impact_new[ind[0]].data['gwp2050']/1e9,impact_new[ind[1]].data['gwp2050']/1e9,impact_new[ind[3]].data['gwp2050']/1e9)
# print("Ren GWP_embodied ", impact_ren[ind[0]].data['gwp2050']/1e9,impact_ren[ind[1]].data['gwp2050']/1e9,impact_ren[ind[3]].data['gwp2050']/1e9)


# %%
# filtered_data = df_var[(df_var['m2 per hab'] == var_rate_m2_per_hab[1]) & (df_var['Renovation rate'] == var_rate_ren[1]) & (df_var['Demolition rate'] == var_rate_dem[1])   & (df_var['Scenario']== 0)  & (df_var['Year 50%']==var_temps50[1])]
# ind = filtered_data.index

# wood_scen0=impact_tot[ind[0]].material['timber'].data_time['kg'][:l_2050]/1e9

# filtered_data = df_var[(df_var['m2 per hab'] == var_rate_m2_per_hab[1]) & (df_var['Renovation rate'] == var_rate_ren[1]) & (df_var['Demolition rate'] == var_rate_dem[1])   & (df_var['Scenario']== 2)  & (df_var['Year 50%']==var_temps50[1])]
# ind = filtered_data.index
# wood_scen2=impact_tot[ind[0]].material['timber'].data_time['kg'][:l_2050]/1e9

# DF = pd.DataFrame(wood_scen0) 
#DF.to_csv("wood_scen0.csv")

# df_var2.to_csv("dataparcoord.csv")

# DF = pd.DataFrame(wood_scen2) 
# DF.to_csv("wood_scen2.csv")


#%%


