#part of this code from threatrace
import torch
import numpy as np
import torch.nn.functional as F
from torch_geometric.nn import  GCNConv
from torch_geometric.data import Data, InMemoryDataset
from gensim.models import Word2Vec
import os.path as osp
from sklearn.preprocessing import StandardScaler
from utils.Word2Vec_embedding import tokenize
from collections import defaultdict
from utils.catrgorize import set_categry

scaler = StandardScaler()

class GNNEncoder(torch.nn.Module):
    def __init__(self, in_channels, hidden_channels, dropout=0.2):
        super(GNNEncoder, self).__init__()
        self.conv1 = GCNConv(in_channels, hidden_channels*2)
        self.conv2 = GCNConv(hidden_channels*2, hidden_channels)
        self.conv3 = GCNConv(hidden_channels, hidden_channels//2)
        self.dropout = dropout  # ذخیره مقدار dropout

    def forward(self, x, edge_index):
        x = self.conv1(x, edge_index)
        x = F.relu(x)
        x = F.dropout(x, p=self.dropout, training=self.training)
        x = self.conv2(x, edge_index)
        x = F.relu(x)
        x = F.dropout(x, p=self.dropout, training=self.training)
        x = self.conv3(x, edge_index)
        return x


class GNNDecoder(torch.nn.Module):
    def __init__(self, hidden_channels, out_channels, dropout=0.2):
        super(GNNDecoder, self).__init__()
        self.linear1 = torch.nn.Linear(hidden_channels//2, hidden_channels)
        self.linear2 = torch.nn.Linear(hidden_channels, hidden_channels*2)
        self.linear3 = torch.nn.Linear(hidden_channels*2, out_channels)
        self.dropout = dropout

    def forward(self, z):
        z = F.relu(self.linear1(z))
        z = F.dropout(z, p=self.dropout, training=self.training)
        z = F.relu(self.linear2(z))
        z = F.dropout(z, p=self.dropout, training=self.training)
        z = self.linear3(z)
        return z
class GNNAutoencoder(torch.nn.Module):
    def __init__(self, in_channels, hidden_channels, dropout=0.2):
        super(GNNAutoencoder, self).__init__()
        self.encoder = GNNEncoder(in_channels, hidden_channels, dropout)
        self.decoder = GNNDecoder(hidden_channels, in_channels, dropout)
    
    def forward(self, x, edge_index):
        z = self.encoder(x, edge_index)
        x_recon = self.decoder(z)
        return x_recon, z

nodeType_map = {
	'Subject' : 0 ,
	'FileObject' : 1 ,
	'NetFlowObject' : 2
}


class TestDataset(InMemoryDataset):
	def __init__(self, data_list):
		super(TestDataset, self).__init__('/tmp/TestDataset')
		self.data, self.slices = self.collate(data_list)

	def _download(self):
		pass
	def _process(self):
		pass




def sentence_vector(sentence , word2vec_model):
	tokens = tokenize(sentence)
	vectors = [word2vec_model.wv[word] for word in tokens if word in word2vec_model.wv]
	return np.mean(vectors, axis=0) if vectors else np.zeros(word2vec_model.vector_size)



def TrainDataset(path , dataset , size , data_type , system):
	node_cnt = 0
	nodeId_map = {}
	feature_dic = {}
	group_dic = {}
	edge_s = []
	edge_e = []
	node_cnt = 0 
	word2vec_model = Word2Vec.load(f'./models/{dataset}/word2vec-embedding_{size}.model')

	feature_file = f"./process_result/{dataset}/{data_type}_uuid2feture.txt"
	set_categry(feature_file , system)
	with open(feature_file, "r" ,  encoding='utf-8') as file:
		for line in file:
			if len(line.split('$')) >3:
				result=line.split('$')
				uuid=result[0]
				group=result[2]
				feature=result[3]
				feature_dic[uuid] =feature
				group_dic[uuid] =group
	file.close
	for now_path in path:
		print(now_path)
		now_path = now_path + '.txt'
		if not osp.exists(now_path): 
			print(now_path + ' not exist! ') 
			continue
		f = open(now_path, 'r')
		for line in f:
			temp = line.strip('\n').split('\t')
			temp=line.strip('\n').split('\t')
			if not (temp[0] in nodeId_map.keys()):
				nodeId_map[temp[0]] =node_cnt
				node_cnt+=1
			temp[0] =nodeId_map[temp[0]]   # src id
			if not (temp[1] in nodeId_map.keys()):
				nodeId_map[temp[1]] =node_cnt
				node_cnt+=1
			temp[1] =nodeId_map[temp[1]]  # dst id
			edge_s.append(temp[0])
			edge_e.append(temp[1])

		f.close()
	x_list = []
	y_list = []
	train_mask = []

	for  uuid , mid in nodeId_map.items():  # number of nodes
			x_list.append(sentence_vector(feature_dic[uuid], word2vec_model))
			y_list.append(int(group_dic[uuid]))
			train_mask.append(True)
	x = torch.tensor(x_list, dtype=torch.float)	#بردار نودها new
	y = torch.tensor(y_list, dtype=torch.int)   #برچسب نودها 


	train_mask = torch.tensor(train_mask, dtype=torch.bool)

	edge_index = torch.tensor([edge_s, edge_e], dtype=torch.long) # ماتریس دو سطری که یال‌ها را نگه می‌دارد
	data1 = Data(x=x, y=y,edge_index=edge_index, train_mask=train_mask) #اطلاعات کامل گراف
	print("Mean:", x.mean().item(), "Std:", x.std().item())
	dataset = TestDataset([data1])  # آماده می‌کنه و در حافظه قرار می‌ده
	return dataset[0]


def TestDatasetA(path ,dataset , size, system):

	node_cnt = 0
	edge_s = []
	edge_e = []
	adj = defaultdict(set)
	nodeId_map = {}
	x_list = []
	y_list = []
	test_mask = []
	feature_dic = {}
	group_dic = {}
	node_cnt = 0 
	with open (f"./groundtruth/{dataset}.txt", "r") as f1:
		GT = set(line.strip() for line in f1)  # تبدیل به مجموعه برای جستجوی سریع

	gt = open (f"./process_result/{dataset}/groundtruth.txt", "w") 
	feature_file = f"./process_result/{dataset}/test_uuid2feture.txt"
	set_categry(feature_file , system)
	with open(feature_file, "r", encoding='utf-8') as file:
		for line in file:
				result = line.split('$')
				uuid = result[0]
				feature_dic[uuid] = result[3]
				group_dic[uuid] = result[2]
				if uuid not in nodeId_map.keys():
					nodeId_map[uuid] = node_cnt
					node_cnt += 1
					if uuid in GT :
						gt.write(uuid+'\n')
	print(node_cnt)
	

	word2vec_model = Word2Vec.load(f'./models/{dataset}/word2vec-embedding_{size}.model')
	for now_path in path:
		print(now_path)
		now_path = now_path + '.txt'
		if not osp.exists(now_path): 
			print(now_path + ' not exist! ') 
			continue
		f = open(now_path, 'r')
		for line in f:
			temp = line.strip('\n').split('\t')
			src = nodeId_map[temp[0]]
			dst = nodeId_map[temp[1]]

			edge_s.append(src)
			edge_e.append(dst)
			adj[dst].add(src)
			adj[src].add(dst)
		f.close()
	
	print(len(nodeId_map))
	for  uuid , mid in nodeId_map.items(): 
		x_list.append(sentence_vector(feature_dic[uuid], word2vec_model))
		y_list.append(int(group_dic[uuid]))
		test_mask.append(True)
	x = torch.tensor(x_list, dtype=torch.float)	#بردار نودها 
	y = torch.tensor(y_list, dtype=torch.int)   #برچسب نودها 
	test_mask = torch.tensor(test_mask, dtype=torch.bool)
	edge_index = torch.tensor([edge_s, edge_e], dtype=torch.long) # ماتریس دو سطری که یال‌ها را نگه می‌دارد
	data1 = Data(x=x, y=y,edge_index=edge_index,  test_mask = test_mask) #اطلاعات کامل گراف
	reversed_nodeId = {v: k for k, v in nodeId_map.items()}
	dataset = TestDataset([data1])
	return dataset[0], adj, reversed_nodeId , feature_dic , data1

