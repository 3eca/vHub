from flask_swagger_ui import get_swaggerui_blueprint


swagger = get_swaggerui_blueprint(
    '/swagger',
    '/static/swagger.json',
    config={'app_name': 'vHub API'}
)


if __name__ == '__main__':
    pass
