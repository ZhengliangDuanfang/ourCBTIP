from flask import Blueprint, request, current_app

from ..plugin import db, siwa
from ..models import User, Drug, Template, Relation
from ..utils.ApiResult import ApiResult
from ..utils.CBTIP import ddi_process
from ..utils.relation_discription import apply_template

import pickle


bp = Blueprint('main', __name__)


@bp.route('/login', methods=['POST'])
@siwa.doc()
def login():
    data = request.get_json()
    print(data)
    name = data.get('name')
    password = data.get('password')

    user = User.query.filter_by(name=name).first()
    if user and user.password == password:
        data = {
            'id': user.id,
            'name': user.name,
        }
        result = ApiResult(code=200, message='Login successful', data=data)
        return result.make_response()
    elif user:
        result = ApiResult(code=401, message='password error')
        return result.make_response()
    else:
        result = ApiResult(code=401, message='Invalid credentials')
        return result.make_response()



@bp.route('/register', methods=['POST'])
@siwa.doc()
def register():
    data = request.get_json()['user_info_dict']
    name = data['name']
    password = data['password']

    user = User.query.filter_by(name=name).first()
    if user:
        result = ApiResult(code=409, message='User name already exists')
        return result.make_response()

    new_user = User(name=name, password=password)
    db.session.add(new_user)
    try:
        db.session.commit()
        data = {
            'id': new_user.id,
            'name': new_user.name,
        }
        result = ApiResult(code=201, message='User created successfully', data=data)
        return result.make_response()
    except Exception as e:
        db.session.rollback()


@bp.route('/ddi', methods=['POST'])
@siwa.doc()
def get_ddi():
    data = request.get_json()
    drug_id_1 = data['drug_id_1']
    drug_id_2 = data['drug_id_2']
    drug_1 = Drug.query.filter_by(drug_id=drug_id_1).first()
    drug_2 = Drug.query.filter_by(drug_id=drug_id_2).first()
    if drug_1 and drug_2:
        drugbank_relations_1 = Relation.query.filter_by(drug_id_1=drug_1.drug_id, drug_id_2=drug_2.drug_id).all()
        drugbank_relations_2 = Relation.query.filter_by(drug_id_1=drug_2.drug_id, drug_id_2=drug_1.drug_id).all()
        drugbank_relations = set()
        for drugbank_relation in drugbank_relations_1:
            drugbank_relations.add(drugbank_relation.relation)
        for drugbank_relation in drugbank_relations_2:
            drugbank_relations.add(drugbank_relation.relation)

        relations = ddi_process(drug_id_1, drug_id_2, current_app.config['SETUPS'])
        predict_relations = []
        for relation in relations:
            if relation not in drugbank_relations:
                predict_relations.append(relation)
        drugbank_relations = list(drugbank_relations)

        drugbank_descriptions = []
        for relation in drugbank_relations:
            template = Template.query.filter_by(relation_id=relation).first()
            description = apply_template(template.template, drug_1.name, drug_2.name)
            drugbank_descriptions.append(description)
        predict_descriptions = []
        for relation in predict_relations:
            template = Template.query.filter_by(relation_id=relation).first()
            description = apply_template(template.template, drug_1.name, drug_2.name)
            predict_descriptions.append(description)



        # with open('./data/ddi', 'rb') as f:
        #     drug_interactions = pickle.load(f)
        # drugbank_relations_1 = drug_interactions[drug_1.drug_id+drug_2.drug_id]
        # drugbank_relations_2 = drug_interactions[drug_2.drug_id+drug_1.drug_id]
        # drugbank_relations = set()
        # for drugbank_relation in drugbank_relations_1:
        #     drugbank_relations.add(drugbank_relation)
        # for drugbank_relation in drugbank_relations_2:
        #     drugbank_relations.add(drugbank_relation)

        # relations = ddi_process(drug_id_1, drug_id_2, current_app.config['SETUPS'])
        # predict_relations = []
        # for relation in relations:
        #     if relation not in drugbank_relations:
        #         predict_relations.append(relation)
        # drugbank_relations = list(drugbank_relations)

        # drugbank_descriptions = []
        # for relation in drugbank_relations:
        #     template = Template.query.filter_by(relation_id=relation).first()
        #     description = apply_template(template.template, drug_1.name, drug_2.name)
        #     drugbank_descriptions.append(description)
        # predict_descriptions = []
        # for relation in predict_relations:
        #     template = Template.query.filter_by(relation_id=relation).first()
        #     description = apply_template(template.template, drug_1.name, drug_2.name)
        #     predict_descriptions.append(description) 
        data = {
            "drugbank_descriptions": drugbank_descriptions,
            "predict_descriptions": predict_descriptions
        }
        return ApiResult(code=200, message='get ddi successfully', data=data).make_response()
    else:
        return ApiResult(code=404, message='Drug not found').make_response()
    

@bp.route('/drug', methods=['POST'])
@siwa.doc()
def get_drug():
    data = request.get_json()
    drug_id = data['drug_id']
    drug = Drug.query.filter_by(drug_id=drug_id).first()
    if drug:
        return ApiResult(code=200, message='get drug successfully', data=drug).make_response()
    else:
        return ApiResult(code=404, message='Drug not found').make_response()


@bp.route('/drugs', methods=['POST'])
@siwa.doc()
def get_drugs():
    drugs = Drug.query.all()
    print(len(drugs))
    drug_list = [
        {
            "id": drug.id,
            "drug_id": drug.drug_id,
            "name": drug.name,
            "type": drug.type
        }
        for drug in drugs
    ]
    return ApiResult(code=200, message='get drugs successfully', data=drug_list).make_response()
