import yaml
from aiohttp import web
import aiohttp_jinja2
import jinja2
import settings
import views
import db as database


class Server:

    def __init__(self, config, dbname='redis'):
        with open(config) as f:
            self._config = yaml.safe_load(f)
        self._dbname = dbname

    async def setup_server(self):
        app = web.Application()
        aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader('./static/'))
        app.router.add_static("/static/", path=".", name="static")
        app['static_root_url'] = "."

        db = await database.DBFactory.get_db(self._dbname, self._config)
        app['db'] = db
        
        app.add_routes([web.post('/', views.handle_shortify),
                        web.get('/', views.handle_index),
                        web.get('/{short_url}', views.handle_redirect)])
        app.on_shutdown.append(self.shutdown_server)
        return app

    async def shutdown_server(self, app):
        app['db'].close()
        await app['db'].wait_closed()

    def run(self):
        web.run_app(self.setup_server(), port=settings.PORT)   


if __name__ == "__main__":
    server = Server('server_conf.yaml')
    server.run()
