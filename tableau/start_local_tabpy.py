"""Launch the pinned TabPy server bound only to 127.0.0.1 for Tableau Desktop.

TabPy 2.16's CLI has no bind-address option. This launcher uses its pinned
application API to bind locally. No public endpoint or live server is packaged.
"""
from pathlib import Path
import sys
import os

# TabPy passes all environment keys to case-insensitive ConfigParser.
# Some Linux runners supply both no_proxy and NO_PROXY; keep the uppercase key.
for name in list(os.environ):
    if name != name.upper() and name.upper() in os.environ:
        del os.environ[name]
import configparser
import logging

from tabpy.tabpy_server.app.app import TabPyApp
from tabpy.tabpy_server.psws.callbacks import init_model_evaluator
import tornado.ioloop

ROOT=Path(__file__).resolve().parents[1]
state=ROOT/'.runtime/tabpy'
state.mkdir(parents=True,exist_ok=True)
settings=configparser.ConfigParser()
settings['TabPy']={
    'TABPY_PORT':'9004',
    'TABPY_STATE_PATH':str(state),
    'TABPY_QUERY_OBJECT_PATH':str(state/'query_objects'),
    'TABPY_EVALUATE_ENABLE':'true',
    'TABPY_LOG_DETAILS':'false',
}
path=state/'local.conf'
with path.open('w') as stream:
    settings.write(stream)
logging.basicConfig(level=logging.WARNING)
# No password is used for this loopback-only classroom connection.
app=TabPyApp(str(path),disable_auth_warning=True)
web=app._create_tornado_web_app()
init_model_evaluator(app.settings,app.tabpy_state,app.python_service)
web.listen(9004,address='127.0.0.1',max_buffer_size=app.max_request_size,max_body_size=app.max_request_size)
print('TabPy ready on 127.0.0.1:9004. Keep this terminal open while using Tableau Desktop.',flush=True)
tornado.ioloop.IOLoop.current().start()
