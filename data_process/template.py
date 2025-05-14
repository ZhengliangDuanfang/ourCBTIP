import os
import pickle
import difflib
from collections import defaultdict

def extract_templates(relations_description):
    templates = {}
    
    for relation_id, sentences in relations_description.items():
        if not sentences:
            continue
            
        # 准备参考句子和分词
        ref_sentence = sentences[0]
        ref_tokens = ref_sentence.split()
        variable_blocks = []
        
        # 收集所有句子的差异块
        for sentence in sentences[1:]:
            current_tokens = sentence.split()
            matcher = difflib.SequenceMatcher(None, ref_tokens, current_tokens)
            blocks = []
            
            for opcode in matcher.get_opcodes():
                tag, i1, i2, j1, j2 = opcode
                if tag != 'equal':
                    blocks.append((i1, i2))
            
            variable_blocks.append(blocks)
        
        # 验证所有差异模式是否一致
        if variable_blocks:
            sample_blocks = variable_blocks[0]
            if not all(blocks == sample_blocks for blocks in variable_blocks):
                continue  # 句式结构不一致则跳过
        else:
            templates[relation_id] = ref_sentence  # 无差异直接使用原句
            continue
        
        # 生成模板
        template_tokens = []
        prev_end = 0
        drug_count = 1
        
        # 按出现顺序处理差异块
        for start, end in sorted(sample_blocks, key=lambda x: x[0]):
            # 添加固定部分
            template_tokens.extend(ref_tokens[prev_end:start])
            # 添加药物占位符
            template_tokens.append(f"[Drug{drug_count}]")
            prev_end = end
            drug_count += 1
        
        # 添加最后部分
        template_tokens.extend(ref_tokens[prev_end:])
        
        # 清理多余空格
        template = " ".join(template_tokens)
        templates[relation_id] = " ".join(template.split())
    
    return templates




if not os.path.exists('./data/relations_discription'):
    # 报错
    print("relation_discription文件不存在")
    exit()

with open('./data/relations_discription', "rb") as f:
    relations_discription = pickle.load(f)

# 每种relation，提取第一个和最后一个句子
sub_relations_description = {}
for relation_id, sentences in relations_discription.items():
    sub_relations_description[relation_id] = sentences[:1] + sentences[-1:]

templates = extract_templates(sub_relations_description)

for rel_id, template in templates.items():
    print(f"Relation {rel_id} Template:")
    print(template)
    print()

with open('./data/templates', "wb") as f:
    pickle.dump(templates, f)