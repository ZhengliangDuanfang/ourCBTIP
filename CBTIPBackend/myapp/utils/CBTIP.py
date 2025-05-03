from ....predict import predict

def ddi_process(drug_id_1, drug_id_2, setup_dict):
    id2target = setup_dict['id2target']
    edges_by_name = []
    for target in id2target.values():
        edges_by_name.append([drug_id_1, drug_id_2, target])
    summary_dict = predict(edges_by_name, setup_dict['decoder_inter'], setup_dict['emb_inter'], setup_dict['drug_cnt'], setup_dict['relation2id'], setup_dict['id2relation'], setup_dict['id2drug'], setup_dict['drug2id'], setup_dict['id2target'], setup_dict['target2id'])
    relations = []
    for prediction in summary_dict:
        if prediction[3] > 0.5:
            relations.append(prediction[2])
    return relations # 返回这两个药物之间所有的relation序号