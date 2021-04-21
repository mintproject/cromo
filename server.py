import connexion

if __name__ == '__main__':
    app = connexion.FlaskApp(__name__, host="localhost", port=8080, specification_dir='openapi/')
    app.add_api('cromo-api.yaml')
    app.run()
