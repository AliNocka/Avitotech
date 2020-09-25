import asyncio
import aioredis
import string
import yaml
import json
from urllib import parse
from aiohttp import web
import aiohttp_jinja2
import jinja2


class Shortener:
    ALPHABET = string.ascii_letters + string.digits

    @staticmethod
    def encode(links_count):
        encoded_chars = []
        while links_count > 0:
            links_count = links_count - 1
            encoded_chars.append(links_count % len(Shortener.ALPHABET))
            links_count //= len(Shortener.ALPHABET)
        encoded_chars = encoded_chars[::-1]
        return ''.join([Shortener.ALPHABET[sym] for sym in encoded_chars])


class Server:

    REDIS_LINKS_COUNT_KEY = "url_count"
    HOST = "localhost"
    PORT = "8080"

    @staticmethod
    def is_valid_url(url):
        parsed_url = parse.urlparse(url)
        return bool(parsed_url.scheme and parsed_url.netloc)

    async def post_handle(self, request):
        data = await request.post()
        redis = request.app['redis']
        url = data.get('url')
        user_url = data.get('user_url')
        if not url:
            return aiohttp_jinja2.render_template('index.html', request, {
                'error': 'Не передан url'
            })
        if not Server.is_valid_url(url):
            return aiohttp_jinja2.render_template('index.html', request, {
                'error': 'Переданный url не является валидным'
            })
        if user_url:
            exists = await redis.get(user_url)
            if exists:
                return aiohttp_jinja2.render_template('index.html', request, {
                    'error': 'Данный url уже занят'
                })
            short_link = user_url
        else:
            short_url = await redis.get(url)
            if short_url:
                return aiohttp_jinja2.render_template('index.html', request, {
                    'shortened_url': '{}:{}/{}'.format(Server.HOST, Server.PORT, short_url.decode('UTF-8'))
                })

            link_count = await redis.incr(Server.REDIS_LINKS_COUNT_KEY)

            short_link = Shortener.encode(link_count)
            exists = await redis.get(short_link)

            while exists:
                link_count = await redis.incr(Server.REDIS_LINKS_COUNT_KEY)
                short_link = Shortener.encode(link_count)
                exists = await redis.get(short_link)

        await redis.set(short_link, url)
        await redis.set(url, short_link)
        return aiohttp_jinja2.render_template('index.html', request, {
                    'shortened_url': '{}:{}/{}'.format(Server.HOST, Server.PORT, short_link)
                })

    async def get_index(self, request):
        return aiohttp_jinja2.render_template('index.html', request, {})

    async def get_handle(self, request):
        redis = request.app['redis']
        short_url = request.match_info.get('short_url')
        if not short_url:
            return web.Response(text='Not found')
        url = await redis.get(short_url)
        return web.HTTPFound(url.decode('UTF-8'))

    async def setup_server(self, config):
        app = web.Application()
        aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader('./static/'))
        redis = await aioredis.create_redis_pool('redis://{}:{}'.format(config['host'], config['port']),\
                                                     db=config['db'], password=config['password'])
        app['redis'] = redis
        
        app.add_routes([web.post('/', self.post_handle),
                        web.get('/', self.get_index),
                        web.get('/{short_url}', self.get_handle)])
        app.on_shutdown.append(self.shutdown_server)
        return app

    async def shutdown_server(self, app):
        app['redis'].close()
        await app['redis'].wait_closed()

    def run(self):
        with open('server_conf.yaml') as f:
            config = yaml.safe_load(f)
        web.run_app(self.setup_server(config))   


if __name__ == "__main__":
    server = Server()
    server.run()

