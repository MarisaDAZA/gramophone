from config import SECRET_KEY, DATABASE_URI
from flask import Flask, request
from gramophone import sub

app = Flask(__name__)
app.secret_key = SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
from db_schema import db
db.init_app(app)
with app.app_context():
    db.create_all()

def check_ip():
    '''检测IP是否来自云湖'''
    if request.headers['User-Agent'] == 'YHChat/QIDAINIDEJIQIREN(NIUBI)' and request.remote_addr in ['82.157.170.175', '192.144.130.26', '8.140.51.215', '81.70.146.99']:
        return True
    else:
        return False

@app.route('/gramophone', methods=['POST'])
def gramophone():
    if check_ip():
       sub.listen(request)
    return ''
