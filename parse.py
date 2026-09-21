import argparse
import json
import os.path as osp
from utils.config import parse_data_list
import time

def get_process_type(value):
    try:
        result= (value.split()[0]).split('/')[-1]       
    except:
        result = "A"
    return result

def parse_data (path_list , data_type  , dataset) :
	print ('start parsing')
	tt = '18' if dataset.split('-')[1] == "e3" else '20'
	type = set()
	seen_nodes = set()
	seen_pairs = set()
	edge_count = 0 
	
	uuid2feture = open(f'./process_result/{dataset}/{data_type}_uuid2feture.txt' , 'w', encoding='utf-8')
	for now_path in path_list:
		if not osp.exists(now_path): 
			print(f'{now_path} not exist')
			continue
		f = open(now_path, 'r' , encoding='utf-8')
		fw = open(now_path+'.txt', 'w')
		print(now_path)

		for line in f:
				data = json.loads(line)  
				datum = data.get("datum", {})
				if f"com.bbn.tc.schema.avro.cdm{tt}.Subject" in datum:
					subject_data = datum[f'com.bbn.tc.schema.avro.cdm{tt}.Subject']
					uuid = subject_data['uuid']
					cmdline_string = subject_data['cmdLine']['string'].split('\n')[0]
					thistype = get_process_type(cmdline_string)
					type.add(thistype)
					seen_nodes.add(uuid)
					uuid2feture.write( uuid + '$' + 'Subject' + '$' + thistype + '$'+ cmdline_string + '$' + now_path + '\n')

				elif f"com.bbn.tc.schema.avro.cdm{tt}.FileObject" in datum:
					file_data = datum[f"com.bbn.tc.schema.avro.cdm{tt}.FileObject"]
					uuid = file_data['uuid']

					try:
						if dataset.split('-')[0] == 'clear': 
							filename_string = file_data["baseObject"]["properties"]["map"]["path"].split('\n')[0]
						else:
							filename_string = file_data["baseObject"]["properties"]["map"]["filename"].split('\n')[0]
						
					except:
						continue	
					uuid2feture.write( uuid + '$' + 'FileObject' + '$' + str (0) + '$'+ filename_string  + '$' + now_path+'\n')
					uuid2feture.flush()
					seen_nodes.add(uuid)
					 

				elif f"com.bbn.tc.schema.avro.cdm{tt}.NetFlowObject" in datum:
					netflow_data = datum[f"com.bbn.tc.schema.avro.cdm{tt}.NetFlowObject"]
					uuid = netflow_data['uuid']
					tt = '18' if dataset.split('-')[1] == "e3" else '20'
					if tt == '18':
						remote_address = netflow_data["remoteAddress"] 
						remote_port = netflow_data["remotePort"]
						local_address = netflow_data["localAddress"] 
						local_port = netflow_data["localPort"] 
					else:
						remote_data = netflow_data.get("remoteAddress", {})  # اگر مقدار None باشد، دیکشنری خالی برمی‌گرداند
						if remote_data:
							remote_address = remote_data.get("string", "")
						else:
							remote_address = ''
						port_data = netflow_data["remotePort"]
						if port_data:
							remote_port = port_data['int']
						else:
							remote_port = ''
						local_data = netflow_data["localAddress"]
						if local_data:
							local_address = local_data['string']
						else:
							local_address=''
						lport_data =  netflow_data["remotePort"]
						if lport_data :
							local_port = lport_data['int']
						else:
							local_port = ''
					if remote_address == '' :
						continue

					seen_nodes.add(uuid)
					net_value = local_address + ' : ' + str(local_port) +  ' to ' +  remote_address + ' : ' + str(remote_port) 
					uuid2feture.write( uuid + '$' + 'NetFlowObject' + '$' + str (0) + '$'+ net_value  + '$' + now_path + '\n')
				
		
				elif f'com.bbn.tc.schema.avro.cdm{tt}.Event' in datum:
					event_data = datum[f'com.bbn.tc.schema.avro.cdm{tt}.Event']
					edgeType = event_data['type']
					timestamp = event_data['timestampNanos']
					srcId = event_data["subject"][f"com.bbn.tc.schema.avro.cdm{tt}.UUID"]
					if srcId not in seen_nodes: 
						continue
					try:
						dstId1 = event_data["predicateObject"][f"com.bbn.tc.schema.avro.cdm{tt}.UUID"]
						if dstId1 in seen_nodes :
							key = (str(srcId), str(dstId1) )
							edge_count +=1
							if  key not in seen_pairs:
								seen_pairs.add(key)
								this_edge1 = str(srcId) + '\t' + str(dstId1) + '\t'+ str(edgeType) + '\t' + str(timestamp) + '\n'
								fw.write(this_edge1)
					except:
						dstId1 = None
					try:
						dstId2 = event_data["predicateObject2"][f"com.bbn.tc.schema.avro.cdm{tt}.UUID"]
						if dstId2 in seen_nodes:
							key = (str(srcId), str(dstId2) )
							if  key not in seen_pairs:
								seen_pairs.add(key)
								this_edge2 = str(srcId) + '\t' + str(dstId2) +  '\t'  + str(edgeType) + '\t' + str(timestamp) + '\n'
								fw.write(this_edge2)
					except: continue


		
		fw.close()
		f.close()
	print(f'node number: {len(seen_nodes)} , edge number: {edge_count}')
	
	uuid2feture.close()

	return type 



def parse_cadets_data (path_list , data_type  , dataset) :
	print ('start parsing')
	tt = '18' if dataset.split('-')[1] == "e3" else '20'
	dir = f'./process_result/{dataset}/'
	type = set()
	seen_nodes = set()
	seen_pairs = set()
	edge_count = 0 
	object_filename = {}
	subjects_cmdline = {}
	uuid2feture = open(f'./process_result/{dataset}/{data_type}_uuid2feture.txt' , 'w', encoding='utf-8')
	for now_path in path_list:
		if not osp.exists(now_path): 
			print(f'{now_path} not exist!')
			continue
		f = open(now_path, 'r' , encoding='utf-8')
		print(now_path)

		for line in f:
				data = json.loads(line)  
				datum = data.get("datum", {})
				if f"com.bbn.tc.schema.avro.cdm{tt}.Subject" in datum:
					subject_data = datum[f'com.bbn.tc.schema.avro.cdm{tt}.Subject']
					uuid = subject_data['uuid']
					subjects_cmdline[uuid]='none'


				elif f"com.bbn.tc.schema.avro.cdm{tt}.FileObject" in datum:
					file_data = datum[f"com.bbn.tc.schema.avro.cdm{tt}.FileObject"]
					uuid = file_data['uuid']
					object_filename[uuid] = 'none'

				elif f"com.bbn.tc.schema.avro.cdm{tt}.NetFlowObject" in datum:
					netflow_data = datum[f"com.bbn.tc.schema.avro.cdm{tt}.NetFlowObject"]
					uuid = netflow_data['uuid']
					tt = '18' if dataset.split('-')[1] == "e3" else '20'
					if tt == '18':
						remote_address = netflow_data["remoteAddress"] 
						remote_port = netflow_data["remotePort"]
						local_address = netflow_data["localAddress"] 
						local_port = netflow_data["localPort"] 
					else:
						remote_data = netflow_data.get("remoteAddress", {})  # اگر مقدار None باشد، دیکشنری خالی برمی‌گرداند
						if remote_data:
							remote_address = remote_data.get("string", "")
						else:
							remote_address = ''
						port_data = netflow_data["remotePort"]
						if port_data:
							remote_port = port_data['int']
						else:
							remote_port = ''
						local_data = netflow_data["localAddress"]
						if local_data:
							local_address = local_data['string']
						else:
							local_address=''
						lport_data =  netflow_data["remotePort"]
						if lport_data :
							local_port = lport_data['int']
						else:
							local_port = ''
					if remote_address == '' :
						continue

					seen_nodes.add(uuid)
					net_value = local_address + ' : ' + str(local_port) +  ' to ' +  remote_address + ' : ' + str(remote_port)
					uuid2feture.write( uuid + '$' + 'NetFlowObject' + '$' + str (0) + '$'+ net_value  + '$' + now_path + '\n')
				
		
				elif f'com.bbn.tc.schema.avro.cdm{tt}.Event' in datum:
					event_data = datum[f'com.bbn.tc.schema.avro.cdm{tt}.Event']
					edgeType = event_data['type']
					timestamp = event_data['timestampNanos']
					if '"subject":null' in line : continue
					srcId = event_data["subject"][f"com.bbn.tc.schema.avro.cdm{tt}.UUID"]
					cmdline = event_data["properties"]["map"].get("exec",'A')
					subjects_cmdline[srcId] = cmdline	 
					if '"predicateObject":null' not in line:
							dstId1 = event_data["predicateObject"][f"com.bbn.tc.schema.avro.cdm{tt}.UUID"]
							if '"predicateObjectPath":null' not in line and '<unknown>' not in line:	
									filename_string = event_data["predicateObjectPath"]["string"]
							else:
									filename_string = 'none'
							if dstId1 in subjects_cmdline.keys() and subjects_cmdline[dstId1] == 'none':
									subjects_cmdline[dstId1] = filename_string
							if dstId1 in object_filename.keys() and object_filename[dstId1] == 'none':
									object_filename[dstId1] = filename_string								


		f.close()
	
	for key , cmdline in subjects_cmdline.items():
		if cmdline == '' or cmdline == 'none': continue
		type.add(cmdline)
		seen_nodes.add(key)
		uuid2feture.write( key + '$' + 'Subject' + '$' + cmdline + '$'+ cmdline + '\n')
	for key , filename in object_filename.items():
		if filename == '' or filename == 'none': continue
		seen_nodes.add(key)
		uuid2feture.write( key + '$' + 'FileObject' + '$' + str (0) + '$'+ filename  + '\n')

	for now_path in path_list:
		if not osp.exists(now_path): continue
		f = open(now_path, 'r' , encoding='utf-8')
		fw = open(now_path+'.txt', 'w')
		print(now_path)

		for line in f:
			data = json.loads(line)  
			datum = data.get("datum", {})
			if f'com.bbn.tc.schema.avro.cdm{tt}.Event' in datum:
					event_data = datum[f'com.bbn.tc.schema.avro.cdm{tt}.Event']
					edgeType = event_data['type']
					timestamp = event_data['timestampNanos']
					if '"subject":null' in line : continue
					srcId = event_data["subject"][f"com.bbn.tc.schema.avro.cdm{tt}.UUID"]
					if srcId not in seen_nodes: 
						continue	 
					if '"predicateObject":null' not in line:
						dstId1 = event_data["predicateObject"][f"com.bbn.tc.schema.avro.cdm{tt}.UUID"]
						if dstId1 in seen_nodes :
							key = (str(srcId), str(dstId1) )
							edge_count +=1
							if  key not in seen_pairs:
								seen_pairs.add(key)
								this_edge1 = str(srcId) + '\t' + str(dstId1) + '\t'+ str(edgeType) + '\t' + str(timestamp) + '\n'
								fw.write(this_edge1)

	uuid2feture.close()
	print(f'node number: {len(seen_nodes)} , edge number: {edge_count}')
	return type 




if __name__ == "__main__":


	parser = argparse.ArgumentParser(description="Example script")
	parser.add_argument("--dataset", type=str, help="[theia-e3,theia-e5,...]")
	args = parser.parse_args()
	assert args.dataset in ['theia-e3','theia-e5','clear-e3','clear-e5','cadets-e3','cadets-e5']
	t1 = time.time()
	dataset = args.dataset
	dir = f'./process_result/{dataset}/'


	train , val , test = parse_data_list(dataset)
	if dataset == 'cadets-e3' or dataset == 'cadets-e5':
		train_subjecttype = parse_cadets_data (train, 'train' , dataset)
		parse_cadets_data (val, 'val' , dataset)
		parse_cadets_data (test , 'test' ,  dataset)
	else:
		train_subjecttype  = parse_data (train, 'train' , dataset)
		parse_data (val, 'val' , dataset)
		parse_data (test , 'test' ,  dataset)
	t2 = time.time()
	print(round(t2 - t1, 2))




