import os
import csv2
import pickle
import xml.etree.ElementTree as ET
from lxml import etree

# 读取 CSV 文件, 获取所有drug的编号, 并保存
def read_csv_file(drug_id_set, file_path):
    with open(file_path, 'r') as csvfile:
        csvreader = csv.DictReader(csvfile)
        for row in csvreader:
            drug1 = row['drug1']
            drug2 = row['drug2']
            if drug1 not in drug_id_set:
                drug_id_set.add(drug1)
            if drug2 not in drug_id_set:
                drug_id_set.add(drug2)


# 获取 drug_id_set
def get_drug_id_set():
    if os.path.exists("./data/drug_set"):
        with open("./data/drug_set", "rb") as f:
            drug_id_set = pickle.load(f)
    else:
        drug_id_set = set()
        read_csv_file(drug_id_set, "./data/CB-DB/ddi_pos.csv")
        read_csv_file(drug_id_set, "./data/CB-DB/ddi_neg.csv")
        # 保存 drug_set
        with open("./data/drug_set", "wb") as f:
            pickle.dump(drug_id_set, f)
    return drug_id_set

def extract_drug_info(xml_file_path):
    # 定义目标路径
    drugbank_id_path_parts = ['drugbank', 'drug', 'drugbank-id']
    name_path_parts = ['drugbank', 'drug', 'name']
    
    # 初始化栈
    tag_stack = []
    elem_stack = []
    
    # 用于存储结果
    drug_info = []
    
    # 用于临时存储当前药物的 ID, name, type
    current_drug_id = None
    current_name = None
    drug_type = None
    
    cnt = 0

    # 解析 XML 数据
    context = etree.iterparse(xml_file_path, events=("start", "end"))
    
    for event, elem in context:
        # 忽略命名空间，只关注标签的本地名称
        tag = etree.QName(elem).localname
        if event == 'start':
            tag_stack.append(tag)
            elem_stack.append(elem)
        elif event == 'end':
            # 检查是否是 drugbank-id 且 primary 属性为 true
            if tag_stack == drugbank_id_path_parts:
                if elem.get('primary') == 'true':
                    current_drug_id = elem.text
            # 检查是否是 name
            elif tag_stack == name_path_parts:
                current_name = elem.text
            # 检查是否是 drug 的结束标签
            elif tag_stack == ['drugbank', 'drug']:
                drug_type = elem.get('type')
                print(cnt)
                cnt += 1
                if current_drug_id and current_name and drug_type:
                    drug_info.append((current_drug_id, current_name, drug_type))
                    current_drug_id = None
                    current_name = None

            
            # 从栈中弹出当前标签和元素
            try:
                tag_stack.pop()
                elem_stack.pop()
            except IndexError:
                pass
            # 清理元素以节省内存
            elem.clear()
            while elem.getprevious() is not None:
                del elem.getparent()[0]
    
    with open('./data/drug_info', 'wb') as f:
        pickle.dump(drug_info, f)

# 获取 drug_set
def get_drug_info():
    if os.path.exists("./data/drug_info"):
        with open("./data/drug_info", "rb") as f:
            drug_info = pickle.load(f)
    else:
        xml_file_path = '../fulldatabase.xml'
        drug_info = extract_drug_info(xml_file_path)
    return drug_info

drug_info = get_drug_info()
drug_id_set = get_drug_id_set()

# 遍历drug_info，如果drug_info的drug_id在drug_id_set中，就保存，否则删除该条记录
filtered_drug_info = [drug for drug in drug_info if drug[0] in drug_id_set]
with open('./data/filtered_drug_info', 'wb') as f:
    pickle.dump(filtered_drug_info, f)
print(len(filtered_drug_info))
print(len(drug_id_set))