import aiohttp_jinja2
import jinja2
import utils
import settings
from aiohttp import web

ERRORS = {
    "without_url": "Не передан url", 
    "invalid_url": "Переданный url не является валидным",
    "busy_url": "Данный url уже занят"
}


async def handle_shortify(request):
    data = await request.post()
    db = request.app['db']
    url = data.get('url')
    user_url = data.get('user_url')
    if not url:
        return aiohttp_jinja2.render_template('index.html', request, {
            'error': ERRORS["without_url"]
        })
    if not utils.is_valid_url(url):
        return aiohttp_jinja2.render_template('index.html', request, {
            'error': ERRORS["invalid_url"]
        })
    if user_url:
        exists = await db.get(user_url)
        if exists:
            return aiohttp_jinja2.render_template('index.html', request, {
                'error': ERRORS["busy_url"]
            })
        short_url = user_url
    else:
        short_url = await db.get(url)
        if short_url:
            return aiohttp_jinja2.render_template('index.html', request, {
                'shortened_url': '{}:{}/{}'.format(settings.HOST, settings.PORT, short_url.decode('UTF-8'))
            })

        link_count = await db.incr(settings.DB_LINKS_COUNT_KEY)

        short_url = utils.encode(link_count)
        exists = await db.get(short_url)

        while exists:
            link_count = await db.incr(settings.DB_LINKS_COUNT_KEY)
            short_url = Shortener.encode(link_count)
            exists = await db.get(short_url)

    await db.set(short_url, url)
    await db.set(url, short_url)
    return aiohttp_jinja2.render_template('index.html', request, {
                'shortened_url': '{}:{}/{}'.format(settings.HOST, settings.PORT, short_url)
            })

async def handle_index(request):
    return aiohttp_jinja2.render_template('index.html', request, {})

async def handle_redirect(request):
    db = request.app['db']
    short_url = request.match_info.get('short_url')
    if not short_url:
        return web.HTTPNotFound()
    url = await db.get(short_url)
    if not url:
        return web.HTTPNotFound()
    return web.HTTPFound(url.decode('UTF-8'))
