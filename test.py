import argparse
import os.path as osp
import os
import argparse
import torch
import re
from torch_geometric.loader import NeighborLoader
from utils.model import * 
from utils.config import get_test_dataset
from collections import Counter
import time
from tqdm import tqdm
import networkx as nx
from torch_geometric.utils import to_networkx
def evaluate (gt ,  alarms , tot_node , print_result=False):
	eps = 1e-10
	tn = 0
	tp = 0
	fn = 0
	fp = 0
	for x in alarms:
		if x in gt: tp +=1
		else : fp +=1
	for x in gt:
		if x not in alarms : fn +=1
	tn = tot_node - tp -fp -fn


	precision = tp/(tp+fp+eps)
	recall = tp/(tp+fn+eps)
	fscore = 2*precision*recall/(precision+recall+eps)
	beta = 2
	beta_sq = beta ** 2	
	fbeta = (1 + beta_sq) * (precision * recall) / ((beta_sq * precision) + recall + eps)
	if print_result:
		print('tp,fp,tn,fn')
		print(tp,fp,tn,fn)
		print('Precision: ', precision)
		print('Recall: ', recall)
		print('F-Score: ', fscore)
		print('Fbeta-Score: ', fbeta)
		# print('MCC: ', mcc)
	return fbeta


if __name__ == "__main__":

	t1 = time.time()
	parser = argparse.ArgumentParser(description="Example script")
	parser.add_argument("--dataset", type=str, default="theia-e3", help="[theia-e3,theia-e5,...]")
	parser.add_argument("-p", type=int, default=100, help="99 or 100")
	args = parser.parse_args()

	name = args.dataset
	percent = args.p


	
	b_size = 1000
	path = get_test_dataset(name)
	graphId = 1
	in_channels = 128
	hidden_channels = 32
	system = 'android' if name.startswith('clear') else 'unix'
	data, adj, nodeID , feature_dic , data1  = TestDatasetA(path , name , in_channels , system)
	
	device = torch.device('cuda')
	
	autoencoder = GNNAutoencoder(in_channels, hidden_channels)
	cat_len = {
			'unix':20,
			'android' : 19
			}
	
	anomaly_threshold  = {}

	with open(f"./models/{name}/thre.txt", "r", encoding="utf-8") as f:  # جایگزین با نام فایل واقعی
		for line in f:
			key, value= line.strip().split(" : ") 
			numbers = re.findall(r'[-+]?\d*\.\d+|\d+', value)
			num = 0 if percent == 99 else 1
			anomaly_threshold [int(key)] = float(numbers[num])

	with open (f"./process_result/{name}/groundtruth.txt", "r") as f1:
		GT = set(line.strip() for line in f1)  # تبدیل به مجموعه برای جستجوی سریع
	alarm =  open(f"./process_result/{name}/alarm.txt", "w" , encoding="utf-8") 
	attack = open(f"./process_result/{name}/attack.txt", "w" , encoding="utf-8") 
	positive = set()
	scores = {}
	reversed_nodeId = {v: k for k, v in nodeID.items()}
	for t in range(cat_len[system]):
		j = t + 1
		anomaly_scores = {}
		for i in range (len(data.test_mask)):
			data.test_mask[i] = False
		
		for i in range (len(data.test_mask)):
				if (data.y[i] == j  ):
					data.test_mask[i] = True
		print('###################################')
		print(data.test_mask.sum().item())
		if (data.test_mask.sum().item() > 0 ):
				model_path = f'./models/{name}/model_'+str(j)
				if os.path.exists(model_path):
					autoencoder.load_state_dict(torch.load(model_path))
				else:
					model_path = f'./models/{name}/model_'+str(cat_len[system])
					anomaly_threshold[j] = anomaly_threshold[cat_len[system]] 
					autoencoder.load_state_dict(torch.load(model_path))
				autoencoder.eval()
				loader = NeighborLoader( data, num_neighbors=[-1, -1 ,-1], batch_size=b_size, input_nodes = data.test_mask, shuffle=False)
				for batch in loader:
					x_recon, z = autoencoder(batch.x, batch.edge_index)
					batch_anomaly_scores = torch.norm(x_recon - batch.x, dim=1)
					y = batch.y.to(device)
					for i, node_id in enumerate(batch.n_id):
						uuid = nodeID[int(node_id)]
						meval = True if (uuid) in GT else False
						score = batch_anomaly_scores[i].item()
						if meval == True and y[i] == j  :
							attack.write(f'{uuid} : {y[i]} : {score} : {anomaly_threshold[j]} : {feature_dic[uuid].strip()}\n')

						if score > anomaly_threshold[j] and   feature_dic[uuid].strip() != ''and reversed_nodeId[uuid] in adj.keys():
							if y[i] == j  :
								positive.add(uuid)
								alarm.write(f'{uuid} $ {y[i]} $ {score} $ {anomaly_threshold[j]} $ {feature_dic[uuid].strip()} $ {meval} \n')
					
	


	print('initial result')
	evaluate( GT , positive , len(data.test_mask), True)
	t2 = time.time()
	print(round(t2 - t1, 2))

	if len(positive) <= 1000 :
		positive_indices = [reversed_nodeId[uuid] for uuid in positive]
		G = to_networkx(data1, to_undirected=True)

		subgraph_nodes = set()

		for i in tqdm( range(len(positive_indices))):
			for j in range(i+1 ,  len(positive_indices)):
				try:
					path = nx.shortest_path(G, positive_indices[i], positive_indices[j])
					subgraph_nodes.update(path)
				except nx.NetworkXNoPath:
					continue

		subgraph_nodes = list(subgraph_nodes)

		subgraph_nodes_original = [int(i) for i in subgraph_nodes]
		final_uuids = [nodeID[i] for i in subgraph_nodes_original]
		print('after_post_process_step1:')
		b1 = evaluate( GT , final_uuids , len(data.test_mask) , True)
	else: 
		print('post_process_step1 ignored!:')
		final_uuids = positive
		b1 = 0 

# تبدیل به UUID
	
	
	second_positive = set ()
	afile  = open('alarm.txt' , 'w')
	mylist = set()
	dic = {}
	for x in final_uuids :
		all_counts = Counter()
		x = reversed_nodeId[x]
		if x in adj.keys():
			for k in adj[x]:
				if nodeID[k] in positive:
					all_counts[k] += 1
				else:
					if k in adj.keys():
						for kk in adj[k]:
							if nodeID[kk] in positive and kk !=x :
								all_counts[kk] += 1		
		# print(len(all_counts))
		dic [nodeID[x]] = (all_counts)
		if len(all_counts) >  2:
			second_positive.add(nodeID[x])
			afile.write(nodeID[x] + '\n')

	print('final result:')
	b2 = evaluate( GT , second_positive , len(data.test_mask), True)

	t2 = time.time()
	print(round(t2 - t1, 2))

