# -*- coding: utf-8 -*-
"""
Created on Wed Aug 16 13:10:00 2023

@author: lucile.schulthe
"""


import pandas as pd
import copy

# default value (see excel for explanation)

m2balconyperera = 0.2
height = 3
rate_wall_s = 0.4
rate_wall = 0.4
building_life=60
h_in=8
h_out=25

fcor=1

save_data=0





def addition_obj(objet1, objet2):
        nouveau_objet = objet1.__class__()

        # Parcourt tous les attributs de l'objet
        for attribut in objet1.__dict__:
            # Vérifie si l'attribut est numérique et peut être additionné
            if isinstance(getattr(objet1, attribut), (int, float)):
                # Additionne les valeurs correspondantes des deux objets et les assigne au nouvel objet
                setattr(nouveau_objet, attribut, getattr(objet1, attribut) + getattr(objet2, attribut))
        
        # Additionne les valeurs des dictionnaires
        for cle, valeur in objet1.__dict__.items():
            if isinstance(valeur, dict):
                nouveau_objet.__dict__[cle] = {k: v + objet2.__dict__[cle][k] for k, v in valeur.items()}

        return nouveau_objet
    
    

    
def multi_obj(objet1, scalar):
        # Crée un nouvel objet avec les mêmes attributs que l'objet actuel
        nouveau_objet = objet1.__class__()

        # Parcourt tous les attributs de l'objet
        for attribut in objet1.__dict__:
            # Vérifie si l'attribut est numérique et peut être multiplié par le scalaire
            if isinstance(getattr(objet1, attribut), (int, float)):
                # Multiplie les valeurs par le scalaire et les assigne au nouvel objet
                setattr(nouveau_objet, attribut, scalar * getattr(objet1, attribut))

        # Multiplie les valeurs des dictionnaires par le scalaire
        for cle, valeur in objet1.__dict__.items():
            if isinstance(valeur, dict):
                nouveau_objet.__dict__[cle] = {k:  v*scalar for k, v in valeur.items()}

        return nouveau_objet    

class Material: # 
    def __init__(self):
        self.data={
            'gwp': 0,
            'gwp2050':0,
            'gwpdyn':0,
            'bio': 0,
            'bio0':0,
            'mat_energy': 0,
            'mat_ren_energy': 0,
            'upb': 0,
            'kg': 0,
            }
    def __add__(self, autre_objet):
       
        return addition_obj(self,autre_objet)
    def __mul__(self, scalar):
        return multi_obj(self,scalar)
        
        
class Phase:
    def __init__(self):
        self.material = {
            'soil': Material(),
            'concrete': Material(),
            'stone': Material(),
            'glass': Material(),
            'timber': Material(),
            'metal': Material(),
            'oil_product': Material(),
            'mineral_fiber': Material(),
            'vegetal_fiber': Material(),

            'gypsum': Material(),
            'equipment': Material(),
            'autre': Material()
        }
        self.data={
            'gwp': 0,
            'gwp2050':0,
            'gwpdyn':0,
            'bio': 0,
            'bio0':0,
            'mat_energy': 0,
            'mat_ren_energy ': 0,
            'upb': 0,
            }
    def __add__(self, autre_objet):
           
        return addition_obj(self,autre_objet)
    def __mul__(self, scalar):
        return multi_obj(self,scalar)
class Surface:
    def __init__(self):
        self.phase = {
            'construction': Phase(),
            'maintenance20': Phase(),
            'maintenance30': Phase(),
            'maintenance40': Phase(),
            'demolition': Phase()
        }

        self.u = 0    # U value -> stay u=0 for not envelope surface
        self.m2 = 0   # m2 of the surface
        
        self.data={
            'gwp': 0,
            'gwp2050':0,
            'gwpdyn':0,
            'bio': 0,
            'bio0':0,
            'mat_energy': 0,
            'mat_ren_energy ': 0,
            'upb': 0,
            }
        
    def __add__(self, autre_objet):
       
        return addition_obj(self,autre_objet)
    def __mul__(self, scalar):
        return multi_obj(self,scalar)        
    
    
    def get_gwp(self, n_phase):
        return sum(c.phase[n_phase].gwp for c in self.material.values())                                # get the gwp for chosen phase

    def get_bio(self, n_phase):                                                                         # get the biogenic carbon for chosen phase
        return sum(c.phase[n_phase].bio * self.m2 for c in self.material.values())


    def get_gwp_per_mat(self, n_phase, type_mat):                                                       # get the gwp for a chosen phase and a chosen material
        self.material[type_mat].phase[n_phase].gwp = self.m2 * self.material[type_mat].phase[n_phase].gwp
        return self.material[type_mat].phase[n_phase].gwp

    def calcul_data(self, outcome):
        self.data[outcome]=0
        for it_phase in self.phase.keys():
            self.data[outcome]+=self.phase[it_phase].data[outcome]

class Envelope(Surface):                                                                                # Envelope surface of the building
    def set_u(self):
        self.u = 0.3

    def annual_consumption(self, degree_day):                                                           # TODO
        self.set_u()
        return self.u * degree_day

class Envelope_ground(Envelope):                                                                        # TODO
    def annual_consumption(self, degree_day):                                                           # TODO
        self.set_u()
        return self.u * 365

class Scenario:
    def __init__(self,name='Default'):
        self.surface = {
            'excavations': Surface(),
            'under_wall': Surface(),
            'foundation': Surface(),
            'out_wall': Envelope(),
            'windows':  Envelope(),
            'roof': Envelope(),
            'era': Surface(),
            'ground': Envelope(),
            'balcony': Surface(),
            'groundroof': Surface(),
            'in_wall_s': Surface(),
            'in_wall': Surface(),
            'in_floor': Surface(),
            'floor': Surface(),
            'underfloor':Surface(),
            'stairs': Surface()
            }
        self.name = name
        
        self.init=0
#        self.set_data(path)
        


    def set_data(self,path):                                                                 # Take the data from xlsx
        if self.init>0:
            self.reinit()
        n = 0
        self.init=1
        data = pd.read_excel(path, sheet_name=self.name)
        df = pd.DataFrame(data, columns=['Surface', 'Material', 'Durée de vie', 'kg/m2FU', 'GWP construction', 'GWP construction 2050', 'GWP demolition','GWP demolition 2050', 'biogenic'])
        self.save_data=df
        for i in range(df[['Surface']].size): 
            
            resultsurf = next((obj for obj in self.surface.keys() if obj == df['Surface'].values[i]),None)  

            if resultsurf is not None:
                # self.surface[resultsurf] Somme du u

                
                resultmat = next((obj for obj in self.surface[resultsurf].phase['construction'].material.keys() if obj == df['Material'].values[i]),None)
                if resultmat is not None:
                    
                    # construction
                    self.surface[resultsurf].phase['construction'].material[resultmat].data['gwp']+=df['GWP construction'].values[i]
                    self.surface[resultsurf].phase['construction'].material[resultmat].data['gwp2050']+=df['GWP construction 2050'].values[i]
                    self.surface[resultsurf].phase['construction'].material[resultmat].data['kg']+=df['kg/m2FU'].values[i]
                    self.surface[resultsurf].phase['construction'].material[resultmat].data['bio']-=df['biogenic'].values[i]
                    self.surface[resultsurf].phase['construction'].material[resultmat].data['bio0']-=df['biogenic'].values[i]   
                    # demolition
                    self.surface[resultsurf].phase['demolition'].material[resultmat].data['gwp']+=df['GWP demolition'].values[i]
                    self.surface[resultsurf].phase['demolition'].material[resultmat].data['gwp2050']+=df['GWP demolition 2050'].values[i]
#                    self.surface[resultsurf].phase['demolition'].material[resultmat].data['kg']-=df['kg/m2FU'].values[i]
                    self.surface[resultsurf].phase['demolition'].material[resultmat].data['bio']+=df['biogenic'].values[i]                 
                    
                    if df['Durée de vie'].values[i]<building_life:
                        if df['Durée de vie'].values[i]==20:
                            self.surface[resultsurf].phase['maintenance20'].material[resultmat].data['gwp']+=(df['GWP construction'].values[i]+df['GWP demolition'].values[i])
                            self.surface[resultsurf].phase['maintenance20'].material[resultmat].data['gwp2050']+=(df['GWP construction 2050'].values[i]+df['GWP demolition 2050'].values[i])
                            self.surface[resultsurf].phase['maintenance20'].material[resultmat].data['kg']+=df['kg/m2FU'].values[i]
                            self.surface[resultsurf].phase['maintenance40'].material[resultmat].data['gwp']+=(df['GWP construction'].values[i]+df['GWP demolition'].values[i])
                            self.surface[resultsurf].phase['maintenance40'].material[resultmat].data['gwp2050']+=(df['GWP construction 2050'].values[i]+df['GWP demolition 2050'].values[i])
                            self.surface[resultsurf].phase['maintenance40'].material[resultmat].data['kg']+=df['kg/m2FU'].values[i]

                            self.surface[resultsurf].phase['maintenance20'].material[resultmat].data['bio0']-=df['biogenic'].values[i] 
                            self.surface[resultsurf].phase['maintenance40'].material[resultmat].data['bio0']-=df['biogenic'].values[i] 
                           
                        elif df['Durée de vie'].values[i]==30 :
                            self.surface[resultsurf].phase['maintenance30'].material[resultmat].data['gwp']+=(df['GWP construction'].values[i]+df['GWP demolition'].values[i])
                            self.surface[resultsurf].phase['maintenance30'].material[resultmat].data['gwp2050']+=(df['GWP construction 2050'].values[i]+df['GWP demolition 2050'].values[i])
                            self.surface[resultsurf].phase['maintenance30'].material[resultmat].data['kg']+=df['kg/m2FU'].values[i]
                            self.surface[resultsurf].phase['maintenance30'].material[resultmat].data['bio0']-=df['biogenic'].values[i]

                        elif df['Durée de vie'].values[i]==40 :
                            self.surface[resultsurf].phase['maintenance40'].material[resultmat].data['gwp']+=(df['GWP construction'].values[i]+df['GWP demolition'].values[i])
                            self.surface[resultsurf].phase['maintenance40'].material[resultmat].data['gwp2050']+=(df['GWP construction 2050'].values[i]+df['GWP demolition 2050'].values[i])
                            self.surface[resultsurf].phase['maintenance40'].material[resultmat].data['kg']+=df['kg/m2FU'].values[i]
                            self.surface[resultsurf].phase['maintenance40'].material[resultmat].data['bio0']-=df['biogenic'].values[i]

                        else :
                           print('erreur ligne:' ,i) 
                            
                      
                        
                elif df['kg/m2FU'].values[i]>0:
                
                    print('erreur ligne:' ,i)
                    print(df['Surface'].values[i])
            else:

                n+=1
    def reinit(self):                                                                   # delete all the data of a surface 
        for key in self.surface.keys():
            self.surface[key]=Surface()                  

    def __add__(self, autre_objet):
       
        return addition_obj(self,autre_objet)
    def __mul__(self, scalar):
        return multi_obj(self,scalar)      

class Scenario_mix(Scenario):
    def set_data_str(self,path):                                                                 # Take the data from xlsx
        if self.init>0:
            self.reinit()
        n = 0
        self.init=1
        data = pd.read_excel(path, sheet_name=self.name)
        df = pd.DataFrame(data, columns=['Surface', 'Material', 'Durée de vie', 'kg/m2FU', 'GWP construction', 'GWP construction 2050', 'GWP demolition', 'GWP demolition 2050', 'biogenic'])
        self.save_data=df
        for i in range(df[['Surface']].size): 
            
            resultsurf = next((obj for obj in self.surface.keys() if obj == df['Surface'].values[i]),None)  

            if resultsurf is not None:
                # self.surface[resultsurf] Somme du u

                
                resultmat = next((obj for obj in self.surface[resultsurf].phase['construction'].material.keys() if obj == df['Material'].values[i]),None)
                if resultmat is not None:
                    
                    if df['Durée de vie'].values[i]==building_life:
                        
                        # construction
                        self.surface[resultsurf].phase['construction'].material[resultmat].data['gwp']+=df['GWP construction'].values[i]                        
                        self.surface[resultsurf].phase['construction'].material[resultmat].data['gwp2050']+=df['GWP construction 2050'].values[i]
                        self.surface[resultsurf].phase['construction'].material[resultmat].data['kg']+=df['kg/m2FU'].values[i]
                        self.surface[resultsurf].phase['construction'].material[resultmat].data['bio']-=df['biogenic'].values[i]
                        self.surface[resultsurf].phase['construction'].material[resultmat].data['bio0']-=df['biogenic'].values[i]
                        # demolition
                        self.surface[resultsurf].phase['demolition'].material[resultmat].data['gwp']+=df['GWP demolition'].values[i]
                        self.surface[resultsurf].phase['demolition'].material[resultmat].data['gwp2050']+=df['GWP demolition 2050'].values[i]
                        self.surface[resultsurf].phase['demolition'].material[resultmat].data['kg']-=df['kg/m2FU'].values[i]
                        self.surface[resultsurf].phase['demolition'].material[resultmat].data['bio']+=df['biogenic'].values[i]       
                            
                      
                        
                elif df['kg/m2FU'].values[i]>0:
                
                    print('erreur ligne:' ,i)
                    print(df['Surface'].values[i])
            else:

                n+=1    

    def set_data_reno(self,path):                                                                 # Take the data from xlsx
        if self.init>0:
            self.reinit()
        n = 0
        self.init=1
        data = pd.read_excel(path, sheet_name=self.name)
        df = pd.DataFrame(data, columns=['Surface', 'Material', 'Durée de vie', 'kg/m2FU', 'GWP construction', 'GWP construction 2050', 'GWP demolition', 'GWP demolition 2050', 'biogenic'])
        self.save_data=df
        for i in range(df[['Surface']].size): 
            
            resultsurf = next((obj for obj in self.surface.keys() if obj == df['Surface'].values[i]),None)  

            if resultsurf is not None:
                # self.surface[resultsurf] Somme du u

                
                resultmat = next((obj for obj in self.surface[resultsurf].phase['construction'].material.keys() if obj == df['Material'].values[i]),None)
                if resultmat is not None:
                    
          
                    
                    if df['Durée de vie'].values[i]<building_life:
                        # construction     
                        self.surface[resultsurf].phase['construction'].material[resultmat].data['gwp']+=df['GWP construction'].values[i]
                        self.surface[resultsurf].phase['construction'].material[resultmat].data['gwp2050']+=df['GWP construction 2050'].values[i]                        
                        self.surface[resultsurf].phase['construction'].material[resultmat].data['kg']+=df['kg/m2FU'].values[i]
                        self.surface[resultsurf].phase['construction'].material[resultmat].data['bio']-=df['biogenic'].values[i]
                        self.surface[resultsurf].phase['construction'].material[resultmat].data['bio0']-=df['biogenic'].values[i]   
                        # demolition
                        self.surface[resultsurf].phase['demolition'].material[resultmat].data['gwp']+=df['GWP demolition'].values[i]
                        self.surface[resultsurf].phase['demolition'].material[resultmat].data['gwp2050']+=df['GWP demolition 2050'].values[i]
                        self.surface[resultsurf].phase['demolition'].material[resultmat].data['kg']-=df['kg/m2FU'].values[i]
                        self.surface[resultsurf].phase['demolition'].material[resultmat].data['bio']+=df['biogenic'].values[i]                            
                        
                        
                        if df['Durée de vie'].values[i]==20:
                            self.surface[resultsurf].phase['maintenance20'].material[resultmat].data['gwp']+=(df['GWP construction'].values[i]+df['GWP demolition'].values[i])
                            self.surface[resultsurf].phase['maintenance20'].material[resultmat].data['gwp2050']+=(df['GWP construction 2050'].values[i]+df['GWP demolition 2050'].values[i])
                            self.surface[resultsurf].phase['maintenance20'].material[resultmat].data['kg']+=df['kg/m2FU'].values[i]
                            self.surface[resultsurf].phase['maintenance40'].material[resultmat].data['gwp']+=(df['GWP construction'].values[i]+df['GWP demolition'].values[i])
                            self.surface[resultsurf].phase['maintenance40'].material[resultmat].data['gwp2050']+=(df['GWP construction 2050'].values[i]+df['GWP demolition 2050'].values[i])
                            self.surface[resultsurf].phase['maintenance40'].material[resultmat].data['kg']+=df['kg/m2FU'].values[i]

                            self.surface[resultsurf].phase['maintenance20'].material[resultmat].data['bio0']-=df['biogenic'].values[i] 
                            self.surface[resultsurf].phase['maintenance40'].material[resultmat].data['bio0']-=df['biogenic'].values[i] 
                           
                        elif df['Durée de vie'].values[i]==30 :
                            self.surface[resultsurf].phase['maintenance30'].material[resultmat].data['gwp']+=(df['GWP construction'].values[i]+df['GWP demolition'].values[i])
                            self.surface[resultsurf].phase['maintenance30'].material[resultmat].data['gwp2050']+=(df['GWP construction 2050'].values[i]+df['GWP demolition 2050'].values[i])
                            self.surface[resultsurf].phase['maintenance30'].material[resultmat].data['kg']+=df['kg/m2FU'].values[i]
                            self.surface[resultsurf].phase['maintenance30'].material[resultmat].data['bio0']-=df['biogenic'].values[i]

                        elif df['Durée de vie'].values[i]==40 :
                            self.surface[resultsurf].phase['maintenance40'].material[resultmat].data['gwp']+=(df['GWP construction'].values[i]+df['GWP demolition'].values[i])
                            self.surface[resultsurf].phase['maintenance40'].material[resultmat].data['gwp2050']+=(df['GWP construction 2050'].values[i]+df['GWP demolition 2050'].values[i])
                            self.surface[resultsurf].phase['maintenance40'].material[resultmat].data['kg']+=df['kg/m2FU'].values[i]
                            self.surface[resultsurf].phase['maintenance40'].material[resultmat].data['bio0']-=df['biogenic'].values[i]

                        else :
                           print('erreur ligne:' ,i) 
                            
                      
                        
                elif df['kg/m2FU'].values[i]>0:
                
                    print('erreur ligne:' ,i)
                    print(df['Surface'].values[i])
            else:

                n+=1

class Archetype: # default init
    def __add__(self,autre_objet):
        return addition_obj(self,autre_objet)
    
    def __init__(self,name='Default',path="database/archetype.xlsx"):

        self.set_data(name,path)
        self.name=name
        
        
    def set_data(self,name,path):
        self.nb_floor = 4
        self.era = 1
        self.shape = 1.5
        self.WWR = 0.3
        self.nb_ss = 1
        
    def set_surface(self,era,bat): 
        
  
        floorarea=era/self.nb_floor
        m2facade=self.shape*era-2*floorarea
        bat.volume = era*height*self.nb_floor

        
        
        bat.surface['excavations'].m2=floorarea*self.nb_ss*height*1.2+0.5*floorarea #underground
        bat.surface['under_wall'].m2=m2facade/self.nb_floor*self.nb_ss #under_wall
        bat.surface['foundation'].m2=floorarea #foundation
        bat.surface['out_wall'].m2=m2facade*(1-self.WWR) #out_wall
        bat.surface['windows'].m2=m2facade*self.WWR #windows      
        bat.surface['roof'].m2=floorarea #roof
        bat.surface['era'].m2=era #era
        bat.surface['ground'].m2=floorarea #ground
        bat.surface['balcony'].m2=era*m2balconyperera #balcony
        
        
        bat.surface['in_wall_s'].m2=era*rate_wall_s #in_wall_s
        bat.surface['in_wall'].m2=era*rate_wall #in_wall
        bat.surface['in_floor'].m2=era-floorarea #in_floor
        bat.surface['floor'].m2=bat.surface['in_floor'].m2+bat.surface['ground'].m2
        bat.surface['underfloor'].m2=floorarea*(self.nb_ss-1) #underfloor

        


class ArchData(Archetype):    


    def set_surface(self,era,bat):


        floorarea=era/self.nb_floor

        m2facade=self.wallrate*(1+self.WWR)*era
        bat.volume = era*height*self.nb_floor
        
        
        bat.surface['excavations'].m2=floorarea*self.nb_ss*height*1.2+0.5*floorarea #underground
        bat.surface['under_wall'].m2=m2facade/self.nb_floor*self.nb_ss #under_wall
        bat.surface['foundation'].m2=floorarea #foundation
        
        bat.surface['out_wall'].m2=self.wallrate*era #out_wall
        
        
        bat.surface['windows'].m2=m2facade*self.WWR #windows      
        bat.surface['roof'].m2=self.roofrate*era #roof
        bat.surface['era'].m2=era #era
        bat.surface['ground'].m2=self.groundrate*era #ground
        
        bat.surface['balcony'].m2=era*m2balconyperera #balcony

        bat.surface['in_wall_s'].m2=era*rate_wall_s #in_wall_s
        bat.surface['in_wall'].m2=era*rate_wall #in_wall
        bat.surface['in_floor'].m2=era-floorarea #in_floor
        bat.surface['floor'].m2=bat.surface['in_floor'].m2+bat.surface['ground'].m2
        bat.surface['underfloor'].m2=floorarea*(self.nb_ss-1) #underfloor
        bat.surface['stairs'].m2=era*self.stairsrate       
        
        
        
    def set_data(self,name,path="database/archetype.xlsx"): 
         path = "database/archetype.xlsx"
         data = pd.read_excel(path)                
         ligne_bat2 = data.loc[data['dataname'] == name]
         
         self.nb=0
         
         self.era = ligne_bat2['era'].values[0]

         self.shape= ligne_bat2['envelope factor'].values[0]
         self.nb_floor=ligne_bat2['number of floors'].values[0]
         # self.height=ligne_bat2['floors height'].values[0]
         

         self.roofrate=ligne_bat2['roof'].values[0]/self.era
         self.wallrate=ligne_bat2['wall'].values[0]/self.era
         self.groundrate=ligne_bat2['floor'].values[0]/self.era
         self.WWR=ligne_bat2['windows ratio'].values[0]
         self.nb_ss=ligne_bat2['nb_ss'].values[0]
         self.stairsrate=ligne_bat2['stairs'].values[0]/self.era      
         
         
#         self.eratot = ligne_bat2['era'].values[0]*ligne_bat2['nb'].values[0]
         self.eratot =ligne_bat2['Surface'].values[0]

         self.heat_tot = ligne_bat2['Heating'].values[0]+ligne_bat2['DHW'].values[0]
         
         self.heat=ligne_bat2['Heating'].values[0]
         self.heat_water=ligne_bat2['DHW'].values[0]
         self.heat_init=ligne_bat2['Heating'].values[0]
         self.heat_water_init=ligne_bat2['DHW'].values[0]
         
         self.periode1=ligne_bat2['Periode1'].values[0]
         self.periode2=ligne_bat2['Periode2'].values[0]
         
         self.heatingsystem={
             'gas': ligne_bat2['Gas'].values[0],
             'oil': ligne_bat2['Fuel oil'].values[0],
             'wood': ligne_bat2['Wood'].values[0]  ,
             'elec': ligne_bat2['Electricity'].values[0],
             'dh': ligne_bat2['District heating'].values[0] ,
             'hp': ligne_bat2['Heat pump'].values[0] ,
             'solar': ligne_bat2['Solar heating'].values[0] ,
             'unknow':0,
             }
         
         self.watersystem={
             'gas': ligne_bat2['DHW_Gas'].values[0],
             'oil': ligne_bat2['DHW_Fuel oil'].values[0],
             'wood': ligne_bat2['DHW_Wood'].values[0]  ,
             'elec': ligne_bat2['DHW_Electricity'].values[0],
             'dh': ligne_bat2['DHW_District heating'].values[0] ,
             'hp': ligne_bat2['DHW_Heat pump'].values[0] ,
             'solar': ligne_bat2['Solar heating'].values[0] ,
             'unknow':0,
             }
         
         self.Qh_li=(ligne_bat2['Qh_lio'].values[0] + ligne_bat2['deltaQh_li'].values[0]*self.shape)*fcor
         self.Qelec=ligne_bat2['Qelec'].values[0]
         self.Qelec_cibles=ligne_bat2['Qelec_cibles'].values[0]
         
class Building:
    def __init__(self,scenario=Scenario(),archetype=Archetype()):

        self.surface =copy.deepcopy(scenario.surface)
        
        self.archetype=archetype              
        self.surface['total']=Surface()
        
        self.archetype_name=archetype.name
        self.scenario_name=scenario.name
        
    def __add__(self,autre_objet):
        return addition_obj(self,autre_objet)
    def __mul__(self, scalar):
        return multi_obj(self,scalar)        
            
    def heat_loss_coeff(self):                                                              # TODO
        return sum(c.m2 * c.u for c in self.surface.values())
    

    def calcul_per_allmat(self,param): 
        # sum the param of each surface per each building and put in the bat.surface['total'] and not in the differents surfaces (but per phase)
        for keypha in self.surface['total'].phase.keys():                             
            for key in self.surface['total'].phase[keypha].material.keys():
                self.surface['total'].phase[keypha].material[key].data[param]= sum(c.phase[keypha].material[key].data[param] * c.m2 for c in self.surface.values())
        
            # also sum all the material together
            self.surface['total'].phase[keypha].data[param]=sum(k.data[param] for k in self.surface['total'].phase[keypha].material.values())            
            
            
    def calcul_per_allmat_surface(self,param):
        for surf in self.surface.keys():
            for keypha in self.surface[surf].phase.keys():

                self.surface[surf].phase[keypha].data[param]=sum(k.data[param] for k in self.surface[surf].phase[keypha].material.values())*self.surface[surf].m2

            self.surface[surf].gwp=sum(self.surface[surf].phase[keypha].data[param] for keypha in self.surface[surf].phase.keys())

    def calcul_surface(self,era):
        self.archetype.set_surface(era,self)



class Town:
    def __init__(self,bat):

        self.bat=bat  #type de bâtiment

        self.bat_tot=Building()
        self.surface=Surface()

                
        
    def set_init(self,m2_build, rate_reno):
        self.m2_build=m2_build #m2 construits
        self.rate_reno=rate_reno
    

    def set_init_surface(self,surface):
        for k in self.bat:
            k.calcul_surface(surface)  
        
    def calcul_surface(self,surface, rate):
        for k in self.bat:
            if rate[self.bat.index(k)]>0 :
                k.calcul_surface(surface*rate[self.bat.index(k)])
        
    def calcul_per_allmat(self,param):
        for k in self.bat:
            k.calcul_per_allmat(param)      
        
        
        


# %%
# To test the classes

# %%  Test archetype

# path="database/archetype.xlsx"
# data = pd.read_excel(path)
# arch=ArchData('MFH1119')

# # # %%


# # # %% 
# path="database/221207_TOOL_2032_BillQuantitiesV5_RénoCésar.xlsx"
# name='Engagé'
# era=1238
# scenario1=Scenario(name)
# scenario1.set_data(path)


# bat1=Building(scenario1, arch)
# bat1.calcul_surface(era)
# bat1.heat_loss_coeff()
# bat1.calcul_per_allmat('gwp')

# ## print(bat1.surface['total'].phase['construction'].material['soil'].data['gwp'])

# print(bat1.surface['total'].phase['construction'].data['gwp']/era)
# print((bat1.surface['total'].phase['maintenance20'].data['gwp']+bat1.surface['total'].phase['maintenance30'].data['gwp']+bat1.surface['total'].phase['maintenance40'].data['gwp'])/era)
# print(bat1.surface['total'].phase['demolition'].data['gwp']/era)




# # # # %%
# print('surface')


# print(bat1.surface['excavations'].m2)
# print(bat1.surface['under_wall'].m2)
# print(bat1.surface['foundation'].m2)
# print(bat1.surface['out_wall'].m2)
# print(bat1.surface['windows'].m2)
# print(bat1.surface['roof'].m2)
# print(bat1.surface['era'].m2)
# print(bat1.surface['ground'].m2)
# print(bat1.surface['balcony'].m2)
# print(bat1.surface['groundroof'].m2)
# print(bat1.surface['in_wall_s'].m2)
# print(bat1.surface['in_wall'].m2)
# print(bat1.surface['in_floor'].m2)
# print(bat1.surface['floor'].m2)
# print(bat1.surface['underfloor'].m2)
# print(bat1.surface['stairs'].m2)



# print('gwp')
# bat1.calcul_per_allmat_surface('gwp')


# print(bat1.surface['excavations'].gwp/era)
# print(bat1.surface['under_wall'].gwp/era)
# print(bat1.surface['foundation'].gwp/era)
# print(bat1.surface['out_wall'].gwp/era)
# print(bat1.surface['windows'].gwp/era)
# print(bat1.surface['roof'].gwp/era)
# print(bat1.surface['era'].gwp/era)
# print(bat1.surface['ground'].gwp/era)
# print(bat1.surface['balcony'].gwp/era)
# print(bat1.surface['groundroof'].gwp/era)
# print(bat1.surface['in_wall_s'].gwp/era)
# print(bat1.surface['in_wall'].gwp/era)
# print(bat1.surface['in_floor'].gwp/era)
# print(bat1.surface['floor'].gwp/era)
# print(bat1.surface['stairs'].gwp/era)


# print('surface maintenance')

# print(bat1.surface['excavations'].phase['maintenance'].data['gwp']/era)
# print(bat1.surface['under_wall'].phase['maintenance'].data['gwp']/era)
# print(bat1.surface['foundation'].phase['maintenance'].data['gwp']/era)
# print(bat1.surface['out_wall'].phase['maintenance'].data['gwp']/era)
# print(bat1.surface['windows'].phase['maintenance'].data['gwp']/era)
# print(bat1.surface['roof'].phase['maintenance'].data['gwp']/era)
# print(bat1.surface['era'].phase['maintenance'].data['gwp']/era)
# print(bat1.surface['ground'].phase['maintenance'].data['gwp']/era)
# print(bat1.surface['balcony'].phase['maintenance'].data['gwp']/era)
# print(bat1.surface['groundroof'].phase['maintenance'].data['gwp']/era)
# print(bat1.surface['in_wall_s'].phase['maintenance'].data['gwp']/era)
# print(bat1.surface['in_wall'].phase['maintenance'].data['gwp']/era)
# print(bat1.surface['in_floor'].phase['maintenance'].data['gwp']/era)
# print(bat1.surface['floor'].phase['maintenance'].data['gwp']/era)
# print(bat1.surface['stairs'].phase['maintenance'].data['gwp']/era)


# print('surface construction')

# print(bat1.surface['excavations'].phase['construction'].data['gwp']/era)
# print(bat1.surface['under_wall'].phase['construction'].data['gwp']/era)
# print(bat1.surface['foundation'].phase['construction'].data['gwp']/era)
# print(bat1.surface['out_wall'].phase['construction'].data['gwp']/era)
# print(bat1.surface['windows'].phase['construction'].data['gwp']/era)
# print(bat1.surface['roof'].phase['construction'].data['gwp']/era)
# print(bat1.surface['era'].phase['construction'].data['gwp']/era)
# print(bat1.surface['ground'].phase['construction'].data['gwp']/era)
# print(bat1.surface['balcony'].phase['construction'].data['gwp']/era)
# print(bat1.surface['groundroof'].phase['construction'].data['gwp']/era)
# print(bat1.surface['in_wall_s'].phase['construction'].data['gwp']/era)
# print(bat1.surface['in_wall'].phase['construction'].data['gwp']/era)
# print(bat1.surface['in_floor'].phase['construction'].data['gwp']/era)
# print(bat1.surface['floor'].phase['construction'].data['gwp']/era)
# print(bat1.surface['stairs'].phase['construction'].data['gwp']/era)


# bat1.calcul_per_allmat_surface('gwp')
# print('surface démolition')

# print(bat1.surface['excavations'].phase['demolition'].data['gwp']/era)
# print(bat1.surface['under_wall'].phase['demolition'].data['gwp']/era)
# print(bat1.surface['foundation'].phase['demolition'].data['gwp']/era)
# print(bat1.surface['out_wall'].phase['demolition'].data['gwp']/era)
# print(bat1.surface['windows'].phase['demolition'].data['gwp']/era)
# print(bat1.surface['roof'].phase['demolition'].data['gwp']/era)
# print(bat1.surface['era'].phase['demolition'].data['gwp']/era)
# print(bat1.surface['ground'].phase['demolition'].data['gwp']/era)
# print(bat1.surface['balcony'].phase['demolition'].data['gwp']/era)
# print(bat1.surface['groundroof'].phase['demolition'].data['gwp']/era)
# print(bat1.surface['in_wall_s'].phase['demolition'].data['gwp']/era)
# print(bat1.surface['in_wall'].phase['demolition'].data['gwp']/era)
# print(bat1.surface['in_floor'].phase['demolition'].data['gwp']/era)
# print(bat1.surface['floor'].phase['demolition'].data['gwp']/era)
# print(bat1.surface['stairs'].phase['demolition'].data['gwp']/era)

# # %% TEst data
# """
# path="database/221207_TOOL_2032_BillQuantitiesV5_NeufKybourg.xlsx"
# name='Réaliste'
# data = pd.read_excel(path, sheet_name=name)
# df = pd.DataFrame(data, columns=['Surface', 'Material', 'Durée de vie', 'kg/m2FU', 'GWP construction', 'GWP demolition', 'biogenic'])


# """