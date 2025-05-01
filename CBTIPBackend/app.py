import click
from flask_migrate import Migrate
import pickle  # 添加导入 pickle

from myapp import create_app
from myapp.plugin import db
from myapp.models import User, Drug, Template


app = create_app()
migrate = Migrate(app, db)


if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1')


@app.cli.command()  # 注册为命令，可以传入 name 参数来自定义命令
def dropall():
    db.drop_all()
    click.echo('Drop tables.')


@app.cli.command()
def init():
    """Initialize the database: Add default user and populate Drug table."""  # 更新文档字符串
    # 在 users 表中添加一条数据
    user = User(
        name='test01',
        password='test0101_'
    )
    db.session.add(user)
    click.echo('Adding default user...')

    # 从文件加载药物数据并填充 Drug 表
    try:
        with open('filtered_drug_info', 'rb') as f:
            drug_data = pickle.load(f)
        click.echo(f'Loaded {len(drug_data)} drug records from file.')

        for drug_id, name, drug_type in drug_data:
            drug = Drug(
                name=name,
                drug_id=drug_id,
                type=drug_type
            )
            db.session.add(drug)
        click.echo('Adding drug data to session...')

        db.session.commit()  # 一次性提交所有更改
        click.echo('Successfully initialized database with default user and drug data.')
    except FileNotFoundError:
        db.session.rollback()  # 如果文件未找到，也需要回滚用户添加
        click.echo('Error: ./data/filtered_drug_info not found. Database initialization failed.')
    except Exception as e:
        db.session.rollback()
        click.echo('Error initializing database: ' + str(e))

    # 向Template表中添加数据
    try:
        with open('templates', 'rb') as f:
            templates = pickle.load(f)
        click.echo(f'Loaded templates.')
        for relation_id, template in templates.items():
            template_item = Template(
                relation_id = relation_id,
                template = template
            )
            db.session.add(template_item)
        db.session.commit()  # 一次性提交所有更改
        click.echo('Successfully initialized database with template data.')
    except FileNotFoundError:
        db.session.rollback()  # 如果文件未找到，也需要回滚用户添加
        click.echo('Error: ./data/templates not found. Database initialization failed.')
    except Exception as e:
        db.session.rollback()
        click.echo('Error initializing database: ' + str(e))