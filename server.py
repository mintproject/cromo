import connexion
from flask_cors import CORS

if __name__ == '__main__':
    app = connexion.FlaskApp(__name__, specification_dir='./openapi/')
    app.add_api('cromo-api.yaml')
    CORS(app.app)
    app.run(port=9090)
