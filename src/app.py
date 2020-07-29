import logging
import api_v1
from flask import Flask, send_from_directory

from context import Context
from cronjob_persister import CronJobPersister
from flask_swagger_ui import get_swaggerui_blueprint


class FlaskLogFilter(logging.Filter):
    def filter(self, record):
        if 'GET /readiness' in record.msg or 'GET /liveness' in record.msg: return False
        return True

# import ptvsd
# ptvsd.enable_attach(address=('0.0.0.0', 5678))
# ptvsd.wait_for_attach()
# ptvsd.break_into_debugger()

app = Flask(__name__, static_url_path='/static')
logger = logging.getLogger('werkzeug')
logger.addFilter(FlaskLogFilter())

context = Context()
context.persister = CronJobPersister()

@app.route('/', methods=['GET'])
def index():
    return app.send_static_file('index.html')


@app.route('/liveness', methods=['GET'])
def liveness():
    return 'OK', 200


@app.route('/readiness', methods=['GET'])
def readiness():
    return 'OK', 200


### swagger specific ###
SWAGGER_URL = '/api/doc'
API_URL = '/static/swagger.json'
SWAGGERUI_BLUEPRINT = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "Connector Config API"
    }
)
app.register_blueprint(SWAGGERUI_BLUEPRINT, url_prefix=SWAGGER_URL)
### end swagger specific ###


app.register_blueprint(api_v1.api, url_prefix='/api/v1')


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=3200, use_reloader=False)
