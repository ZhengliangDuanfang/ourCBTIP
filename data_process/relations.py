import os
import csv
import pickle
import xml.etree.ElementTree as ET
from lxml import etree

# 读取 ddi_pos.csv的数据，将信息yongyong
def parse_ddi_pos():
    if os.path.exists("./data/ddi"):
        with open("./data/ddi", "rb") as f:
            ddi_dict = pickle.load(f)
        return ddi_dict
    ddi_dict = {}
    with open("./data/CB-DB/ddi_pos.csv") as csvfile:
        csvreader = csv.DictReader(csvfile)
        for row in csvreader:
            drug1 = row['drug1']
            drug2 = row['drug2']
            type  = int(row['type'])
    
            if drug2 not in ddi_dict:
                ddi_dict[drug2] = {}
            if drug1 not in ddi_dict[drug2]:
                ddi_dict[drug2][drug1] = {}
                ddi_dict[drug2][drug1]["type"] = type

        # 计算总数
        total_interactions = sum(len(ddi_dict[drug]) for drug in ddi_dict)
        print(f'Total interactions: {total_interactions}')

    with open("./data/ddi", "wb") as f:
        pickle.dump(ddi_dict, f)

def extract_drug_interactions(xml_file_path):
    ddi_dict = parse_ddi_pos()
    cnt = 0

    # 定义目标路径
    drugbank_id_path = ['drugbank', 'drug', 'drugbank-id']
    interaction_path = ['drugbank', 'drug', 'drug-interactions', 'drug-interaction']
    
    # 初始化解析状态
    tag_stack = []
    elem_stack = []
    current_drug_id = ""
    current_interaction = {}
    
    # 流式解析XML
    context = etree.iterparse(xml_file_path, events=("start", "end"))
    
    for event, elem in context:
        tag = etree.QName(elem).localname
        
        if event == 'start':
            tag_stack.append(tag)
            elem_stack.append(elem)
        elif event == 'end':
            try:
                # 捕获主药物ID
                if tag_stack == drugbank_id_path and elem.get('primary') == 'true':
                    current_drug_id = elem.text
                
                # 捕获互作用信息
                if tag_stack == interaction_path + ['drugbank-id']:
                    current_interaction['drugbank_id'] = elem.text
                if tag_stack == interaction_path + ['name']:
                    current_interaction['name'] = elem.text
                if tag_stack == interaction_path + ['description']:
                    current_interaction['description'] = elem.text
                
                # 当完成一个互作用条目时保存
                if tag == 'drug-interaction':
                    if current_drug_id in ddi_dict and current_interaction['drugbank_id'] in ddi_dict[current_drug_id]:
                        ddi_dict[current_drug_id][current_interaction['drugbank_id']]["description"] = current_interaction['description']
                        ddi_dict[current_drug_id][current_interaction['drugbank_id']]["name"] = current_interaction['name']
                        cnt += 1
                        print(f'{cnt}/1119513')

                # 清理已处理元素
                elem.clear()
                while elem.getprevious() is not None:
                    del elem.getparent()[0]
                
            finally:
                tag_stack.pop()

    with open("./data/relations", "wb") as f:
        pickle.dump(ddi_dict, f)
    
    return ddi_dict


# 获取 drug_set
def get_relations():
    if os.path.exists("./data/relations"):
        with open("./data/relations", "rb") as f:
            ddi_dict = pickle.load(f)
    else:
        xml_file_path = '../fulldatabase.xml'
        ddi_dict = extract_drug_interactions(xml_file_path)
    return ddi_dict

ddi_dict = get_relations()

relations_set = set()
for drug1 in ddi_dict:
    for drug2 in ddi_dict[drug1]:
        type = ddi_dict[drug1][drug2]["type"]
        relations_set.add(type)

# 得到每个互作用他们的名称，首先对ddi_dict进行分类，得到每类互作用与其有关的名称
relations_discription = {i : [] for i in relations_set}
for drug1 in ddi_dict:
    for drug2 in ddi_dict[drug1]:
        type = ddi_dict[drug1][drug2]["type"]
        relations_discription[type].append(ddi_dict[drug1][drug2]["description"])

with open("./data/relations_discription", "wb") as f:
    pickle.dump(relations_discription, f)