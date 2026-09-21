
import argparse
import torch
import torch_geometric
from torch_geometric.loader import NeighborLoader
from utils.model import *
from utils.config import *
from utils.Word2Vec_embedding import train_word2vec
import shutil
import numpy as np
import time

import random
def test(loader ,dataset_name , j ):
	model_path = f'./models/{dataset_name}/model_'+str(j)
	model = GNNAutoencoder(in_channels, hidden_channels)
	model.load_state_dict(torch.load(model_path))
	model.eval()
	all_scores = []
	for batch in loader:
		x_recon, z = model(batch.x, batch.edge_index)
		batch_anomaly_scores = torch.norm(x_recon - batch.x, dim=1)
		batch_scores = batch_anomaly_scores.detach().cpu().numpy()  # یا .tolist()
		all_scores.extend(batch_scores)
	return np.percentile(all_scores, 99),max (all_scores)
	
# # آموزش مدل با Mini-Batch
def train_function(loader, j, name ,epochs):
	seed = 0
	random.seed(seed)
	np.random.seed(seed)
	torch.manual_seed(seed)
	torch.cuda.manual_seed_all(seed)
	torch_geometric.seed_everything(seed)
	torch.backends.cudnn.deterministic = True
	torch.backends.cudnn.benchmark = False
	model = GNNAutoencoder(in_channels, hidden_channels , dr)
	optimizer = torch.optim.Adam(model.parameters(), lr=0.001, weight_decay=5e-4)
	criterion = torch.nn.MSELoss(reduction='mean')
	model.train()
	best_loss = float('inf')
	min_delta = 1e-4  # حداقل تغییر مورد نیاز
    
	for epoch in range(epochs):
		total_loss = 0
		for batch in loader:
			optimizer.zero_grad()
			x_recon, z = model(batch.x, batch.edge_index)
			loss = criterion(x_recon, batch.x)  # فقط روی batch
			loss.backward()
			optimizer.step()
			total_loss += loss.item() * batch.batch_size
		avg_loss = total_loss / len(loader)
		print(f'Epoch {epoch}, Loss: {avg_loss:.4f} ')
		if avg_loss < best_loss - min_delta:
			best_loss = avg_loss
			torch.save(model.state_dict(), f'./models/{name}/model_{j}')

if __name__ == "__main__":
	global b_size, args, thre  , dr ,optimizer, device , criterion , hidden_channels , in_channels
	t1 = time.time()
	parser = argparse.ArgumentParser(description="Example script") 
	parser.add_argument("--dataset", type=str, help="[theia-e3,theia-e5,...]")
	parser.add_argument("-dr", type=float, default=0.2)  #cl3 = 0.05 , th3 = 0.05
	args = parser.parse_args()
	dataset_name = args.dataset
	dr = args.dr

	b_size = 1000
	system = 'android' if dataset_name.startswith('clear') else 'unix'
	cat_len = {
			'unix':20,
			'android' : 19
			}
	# train = f"./process_result/{dataset_name}/train_uuid2feture.txt"
	
	# train_corpus = []
	# file = open(train, "r", encoding="utf-8") 
	# lines = file.readlines()
	# for line in lines :
	# 	row = line.split('$')
	# 	if len(row) >= 3 :
	# 		train_corpus.append(row[3])
	# train_word2vec(train_corpus  , dataset_name ,128)
	thre_file =  open(f"./models/{dataset_name}/thre.txt", "w")
	train_path = get_train_dataset(dataset_name)
	val_path = get_val_dataset(dataset_name)
	in_channels = 128
	hidden_channels = 32
	train_data = TrainDataset(train_path , dataset_name , in_channels , 'train' , system)
	val_data = TrainDataset(val_path , dataset_name , in_channels , 'val' , system)
	device = torch.device('cuda')

	for t in range(cat_len[system]):
		j = t + 1
		print(f'model number {j}')
		for i in range (len(train_data.train_mask)):
			train_data.train_mask[i] = False
		 
		for i in range (len(train_data.train_mask)):
			if (train_data.y[i] == j ):
				train_data.train_mask[i] = True

		for i in range (len(val_data.train_mask)):
			val_data.train_mask[i] = False
		 
		for i in range (len(val_data.train_mask)):
			if (val_data.y[i] == j ):
				val_data.train_mask[i] = True
		print(train_data.train_mask.sum().item())
		if train_data.train_mask.sum().item() == 0 : continue

		train_loader = NeighborLoader(
    		train_data, 
    		num_neighbors=[-1, -1 , -1 ], 
    		batch_size=b_size,  
   			input_nodes=train_data.train_mask, 
    		shuffle=False
			)

		val_loader = NeighborLoader(
    		val_data,
   			num_neighbors=[-1, -1, -1],
    		batch_size=b_size,
    		input_nodes=  val_data.train_mask , 
    		shuffle=False)
		train_function( train_loader , j , dataset_name ,70)
		if val_data.train_mask.sum().item()  > 0 :
			thre1  = test(val_loader , dataset_name , j )
		else:
			thre1 = test(train_loader , dataset_name , j )
		thre_file.write(f'{j} : {thre1}\n')

	t2 = time.time()
	print(round(t2 - t1, 2))
