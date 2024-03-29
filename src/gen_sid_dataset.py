import os
from pathlib import Path

from util import utils_data

print("Generate synthetic segmentation dataset.")

root_dir = Path(__file__).resolve().parents[1]
save_path = os.path.join(root_dir, 'Data/SID_1t20_train/') # save in folder

past = 4
minT = 1
maxT = 20
sim_time_per_scene = 10 # times, 10,2
index_list = list(range(1,11)) # list(range(1,11)) # 1~10 # [1,3,5] a simple crossing

utils_data.save_SID_data(index_list, save_path, sim_time_per_scene)
print('CSV records for each index generated.')

utils_data.gather_all_data_trajectory(save_path, past, maxT=maxT, minT=minT) # go through all the obj folders and put them together in one CSV
print('Final CSV generated!')
