import os
from pathlib import Path

import random
import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
import matplotlib.patches as patches

from multiple_scene_multimodal_dataset import msmd_object # this is static env
from single_interaction_dataset import sid_object         # this is dynamic env

def gen_csv_trackers(data_dir:str): # this is only used for dynamic environment
    # all trajectories under one index
    obj_folders = os.listdir(data_dir) # all files named by indices
    for objf in obj_folders:
        obj_files = os.listdir(os.path.join(data_dir, objf)) # all files/images under this folder
        t_list = []   # time or time step
        id_list = []
        x_list = []   # x coordinate
        y_list = []   # y coordinate
        idx_list = [] # more information (e.g. scene index)
        invalid_files = []
        for f in obj_files:
            info = f[:-4] # the last for characters are filename extensions
            try:
                idx_list.append(int(info.split('_')[0]))
                t_list.append(int(info.split('_')[1]))
                x_list.append(float(info.split('_')[2]))
                y_list.append(float(info.split('_')[3]))
                id_list.append(objf)
            except:
                invalid_files.append(f)
                continue
        for f in invalid_files:
            obj_files.remove(f)
        df = pd.DataFrame({'f':obj_files, 't':t_list, 'id':id_list, 'index':idx_list, 'x':x_list, 'y':y_list}).sort_values(by='t', ignore_index=True)
        df.to_csv(os.path.join(data_dir, objf, 'data.csv'), index=False)

def gather_all_data_position(data_dir:str, past:int, maxT:int, minT:int=1, period:int=1, save_dir:str=None, dynamic_env:bool=False):
    # data_dir - index - img&csv
    if save_dir is None:
        save_dir = data_dir

    if dynamic_env: # if dynamic env,  'f' means an image file
        csv_str = 'f'
    else:           # else static env, 't' means the time step
        csv_str = 't'

    column_name = [f'{csv_str}{i}' for i in range(0,past+1)] + ['id', 'index', 'T', 'x', 'y']
    df_all = pd.DataFrame(columns=column_name)
    obj_folders = os.listdir(data_dir)
    cnt = 0
    for objf in obj_folders:
        cnt += 1
        print(f'\rProcess {cnt}/{len(obj_folders)}', end='    ')
        df_obj = pd.read_csv(os.path.join(data_dir, objf, 'data.csv')) # generated by "gen_csv_trackers"
        for T in range(minT,maxT+1):
            sample_list = []
            for i in range(len(df_obj)-past*period-T): # each sample
                sample = []
                ################## Sample START ##################
                for j in range(past+1):
                    obj_past = df_obj.iloc[i+j*period][csv_str]
                    sample.append(obj_past)
                sample.append(df_obj.iloc[i+past+T]['id'])
                sample.append(df_obj.iloc[i+past+T]['index'])
                sample.append(T)
                sample.append(df_obj.iloc[i+past+T]['x'])
                sample.append(df_obj.iloc[i+past+T]['y'])
                ################## Sample E N D ##################
                sample_list.append(sample)
            df_T = pd.DataFrame(sample_list, columns=df_all.columns)
            df_all = pd.concat([df_all, df_T], ignore_index=True)
    df_all.to_csv(os.path.join(save_dir, 'all_data.csv'), index=False)

def gather_all_data_trajectory(data_dir:str, past:int, maxT:int, minT:int=1, period:int=1, save_dir:str=None, dynamic_env:bool=False):
    if save_dir is None:
        save_dir = data_dir

    if dynamic_env: # if dynamic env,  'f' means an image file
        csv_str = 'f'
    else:           # else static env, 't' means the time step
        csv_str = 't'

    column_name = [f'{csv_str}{i}' for i in range(0,(past+1))] + ['id', 'index'] + [f'T{i}' for i in range(minT, maxT+1)]
    df_all = pd.DataFrame(columns=column_name)
    obj_folders = os.listdir(data_dir)
    cnt = 0
    for objf in obj_folders:
        cnt += 1
        print(f'\rProcess {cnt}/{len(obj_folders)}', end='    ')
        df_obj = pd.read_csv(os.path.join(data_dir, objf, 'data.csv')) # generated by "gen_csv_trackers"
        
        sample_list = []
        for i in range(len(df_obj)-past*period-maxT): # each sample
            sample = []
            ################## Sample START ##################
            for j in range(past+1):
                obj_past = df_obj.iloc[i+j*period][csv_str]
                sample.append(obj_past)
            sample.append(df_obj.iloc[i+past+maxT]['id'])
            sample.append(df_obj.iloc[i+past+maxT]['index'])
            for T in range(minT, maxT+1):
                sample.append(f'{df_obj.iloc[i+past+T]["x"]}_{df_obj.iloc[i+past+T]["y"]}')
            ################## Sample E N D ##################
            sample_list.append(sample)
        df_T = pd.DataFrame(sample_list, columns=df_all.columns)
        df_all = pd.concat([df_all, df_T], ignore_index=True)
    df_all.to_csv(os.path.join(save_dir, 'all_data.csv'), index=False)

def save_fig_to_array(fig, save_path):
    import matplotlib
    import pickle
    matplotlib.use('agg')
    fig.tight_layout(pad=0)
    fig.canvas.draw()
    fig_in_np = np.frombuffer(fig.canvas.tostring_rgb(), dtype=np.uint8)
    fig_in_np = fig_in_np.reshape(fig.canvas.get_width_height()[::-1] + (3,))
    with open(save_path, 'wb') as f:
        pickle.dump(fig_in_np, f)


def save_MSMD_data(index_list:list, save_path:str, sim_time_per_scene:int):
    # MSMD - Multiple Scene Multimodal Dataset
    cnt = 0 # used as ID here
    overall_sim_time = sim_time_per_scene * len(index_list)
    for idx in index_list:
        boundary_coords, obstacle_list, nchoices = msmd_object.return_Map(index=idx) # map parameters
        ts = 0.2
        
        ### For each index, save one static environment
        graph = msmd_object.Graph(boundary_coords, obstacle_list, inflation=0)
        _, ax = plt.subplots()
        graph.plot_map(ax, clean=True) ### NOTE change this
        ax.set_aspect('equal', 'box')
        ax.axis('off')
        if save_path is None:
            plt.show()
        else:
            folder = os.path.join(save_path, f'{idx}/')
            Path(folder).mkdir(parents=True, exist_ok=True)
            plt.savefig(os.path.join(folder,f'{idx}.png'), 
                        bbox_inches='tight', pad_inches=0)
            plt.close()

        t_list = []   # time or time step
        id_list = []
        x_list = []   # x coordinate
        y_list = []   # y coordinate
        idx_list = [] # more information (e.g. scene index)
        
        t = 0 # accumulated time for each scene (index)
        choice_list = list(range(1,nchoices+1))
        for ch in choice_list:
            for i in range(sim_time_per_scene//nchoices):
                cnt += 1
                print(f'\rSimulating: {cnt}/{overall_sim_time}   ', end='')
                stagger = 0.4   + (random.randint(0, 20)/10-1) * 0.2
                vmax = 1        + (random.randint(0, 20)/10-1) * 0.3
                ref_path = msmd_object.get_ref_path(index=idx, choice=ch, reverse=(i<((sim_time_per_scene//nchoices)//2)))

                obj = msmd_object.MovingObject(ref_path[0], stagger=stagger)
                obj.run(ref_path, ts, vmax)

                ### Generate images
                for tr in obj.traj:
                    idx_list.append(idx)
                    t_list.append(t)
                    x_list.append(tr[0])
                    y_list.append(tr[1])
                    id_list.append(cnt)
                    t += 1
        df = pd.DataFrame({'t':t_list, 'id':id_list, 'index':idx_list, 'x':x_list, 'y':y_list}).sort_values(by='t', ignore_index=True)
        df.to_csv(os.path.join(save_path, f'{idx}/', 'data.csv'), index=False)
    print()

def save_SID_data(index_list:list, save_path:str, sim_time_per_scene:int):
    # SID - Single-target Interaction Dataset
    def index2map(index):
        # index: [map_idx, path_idx, interact]
        assert (12>=index>=1),("Index must be an integer from 1 to 12.")
        map_dict = {1:[1,1,False], 2:[1,1,True],
                    3:[1,2,False], 4:[1,2,True],
                    5:[1,3,False], 6:[1,3,True],

                    7: [2,1,False], 8: [2,1,True],
                    9: [2,2,False], 10:[2,2,True],
                    11:[2,3,False], 12:[2,3,True]
                    }
        return map_dict[index]
    cnt = 0
    overall_sim_time = sim_time_per_scene * len(index_list)
    for idx in index_list:
        map_idx, path_idx, interact = index2map(idx) # map parameters
        stagger, vmax, target_size, ts = (0.2, 1, 0.5, 0.2) # object parameters

        graph = sid_object.Graph(map=map_idx, block=False)
        path  = graph.get_path(path_idx)
        if interact:
            dyn_obs_path = graph.get_obs_path(ts)
        else:
            dyn_obs_path = [(-1,-1)]

        for _ in range(sim_time_per_scene):
            cnt += 1
            print(f'\rSimulating: {cnt}/{overall_sim_time}', end='   ')

            obj = sid_object.MovingObject(path[0], stagger)
            obj.run(path, ts, vmax, dyn_obs_path=dyn_obs_path)
            for j, tr in enumerate(obj.traj):
                obs_idx = min(j, len(dyn_obs_path)-1)
                obs_shape = patches.Circle(dyn_obs_path[obs_idx], radius=target_size/2, fc='k')

                # images containing everything
                _, ax = plt.subplots()
                graph.plot_map(ax, clean=True) ### NOTE change this
                ax.add_patch(obs_shape)
                ax.set_aspect('equal', 'box')
                ax.axis('off')
                if save_path is None:
                    plt.show()
                else:
                    folder = os.path.join(save_path,f'{cnt}/')
                    Path(folder).mkdir(parents=True, exist_ok=True)
                    plt.savefig(os.path.join(folder,f'{idx}_{j}_{round(tr[0],4)}_{round(tr[1],4)}.png'), 
                                bbox_inches='tight', pad_inches=0)
                    plt.close()
    print()
