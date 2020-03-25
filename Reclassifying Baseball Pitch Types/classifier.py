from pybaseball import playerid_reverse_lookup, statcast_pitcher, statcast_batter
import pickle
import pandas as pd
import numpy as np

class recommend():
    def __init__(self):
        self.modelR = pickle.load(open("modelr.p","rb"))
        self.scalerR = pickle.load(open("scalerr.p","rb"))
        self.modelL = pickle.load(open("modell.p","rb"))
        self.scalerL = pickle.load(open("scalerl.p","rb"))
        self.fgp = pd.read_csv('fgpitchers.csv')
        self.fgh = pd.read_csv('fghitters.csv')
        
    def pitcherlist(self):
        return self.fgp
    
    def batterlist(self):
        return self.fgh
        
    def pitcher(self,name,team):
        Xcols = ['pfx_x','pfx_z','release_speed','release_spin_rate']
        
        fgp = self.fgp
        player = fgp[(fgp.Name.str.lower() == name.lower()) & 
                     (fgp.Team.str.lower() == team.lower())].playerid
        pid = int(playerid_reverse_lookup(player,'fangraphs').key_mlbam)
        pitch = statcast_pitcher(start_dt='2015-03-28',
                                 end_dt='2019-09-29',
                                 player_id=pid)
        if set(pitch.p_throws) == {'R'}:
            throws = 'R'
            scaler = self.scalerR
            kmeans = self.modelR
        else:
            throws = 'L'
            scaler = self.scalerL
            kmeans = self.modelL
        pitch.dropna(subset=Xcols, inplace=True)
        pitch.reset_index(drop=True,inplace=True)
        pitch['p_type'] = kmeans.predict(scaler.transform(pitch[Xcols]))
        pitchdict = {}
        for i in range(13):
            if throws == 'R':
                if i == 7:
                    pitchernum = pitch[(pitch.p_type == 7) | (pitch.p_type == 12)]
                elif i == 12:
                    pitchernum = []
                else:
                    pitchernum = pitch[pitch.p_type == i]
            else:
                if i == 0:
                    pitchernum = pitch[(pitch.p_type == 0) | (pitch.p_type == 4)]
                elif i == 4:
                    pitchernum = []
                else:
                    pitchernum = pitch[pitch.p_type == i]
            cutoff = len(pitchernum) / len(pitch)
            if cutoff > (1/20):
                pitchdict[i] = round((cutoff * 100), 1)
        return pid, pitchdict, throws
    
    def batter(self,name,team,throws='R'):
        Xcols = ['pfx_x','pfx_z','release_speed','release_spin_rate']
        if throws == 'R':
            scaler = self.scalerR
            kmeans = self.modelR
        else:
            scaler = self.scalerL
            kmeans = self.modelL
        fgh = self.fgh
        player = fgh[(fgh.Name.str.lower() == name.lower()) & 
                     (fgh.Team.str.lower() == team.lower())].playerid
        pid = int(playerid_reverse_lookup(player,'fangraphs').key_mlbam)
        bat = statcast_batter(start_dt='2015-03-28',
                              end_dt='2019-09-29',
                              player_id=pid)
        bat.dropna(subset=Xcols, inplace=True)
        bat.reset_index(drop=True,inplace=True)
        bat = bat[bat.p_throws == throws]
        bat['p_type'] = kmeans.predict(scaler.transform(bat[Xcols]))
        batdict = {}
        for i in range(12):
            if throws == 'R':
                if i == 7:
                    batnum = bat[(bat.p_type == 7) | (bat.p_type == 12)]
                elif i == 12:
                    continue
                else:
                    batnum = bat[bat.p_type == i]
            else:
                if i == 0:
                    batnum = bat[(bat.p_type == 0) | (bat.p_type == 4)]
                elif i == 4:
                    continue
                else:
                    batnum = bat[bat.p_type == i]
            batdict[i] = [len(batnum)]
            batdict[i] += [round((np.sum(batnum.woba_value) / np.sum(batnum.woba_denom)),3)]
        return pid, batdict