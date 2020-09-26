from aiohttp.test_utils import AioHTTPTestCase, unittest_run_loop
from aiohttp import web
import unittest

import utils
from server import Server
from views import ERRORS


class UtilsTest(unittest.TestCase):

	def test_encoder(self):
		self.assertEqual(utils.encode(1), 'a')
		self.assertEqual(utils.encode(2), 'b')
		self.assertEqual(utils.encode(63), 'aa')

	def test_url_validator(self):
		self.assertEqual(utils.is_valid_url('http://example.org/some_path'), True)
		self.assertEqual(utils.is_valid_url('invalid_url'), False)


class ServerTest(AioHTTPTestCase):

	async def get_application(self):
		server = Server('server_conf.yaml', 'local')
		app = await server.setup_server()
		return app

	@unittest_run_loop
	async def test_index(self):
		resp = await self.client.request('GET', '/')
		self.assertEqual(resp.status, 200)
	
	@unittest_run_loop
	async def test_not_found(self):
		resp = await self.client.request('GET', '/notfound')
		self.assertEqual(resp.status, 404)

	@unittest_run_loop
	async def test_without_url(self):
		resp = await self.client.request('POST', '/')
		self.assertEqual(resp.status, 200)
		text = await resp.text()
		self.assertEqual(ERRORS["without_url"] in text, True)

	@unittest_run_loop
	async def test_invalid_url(self):
		resp = await self.client.post('/', data={"url": "invalid_url"})
		self.assertEqual(resp.status, 200)
		text = await resp.text()
		self.assertEqual(ERRORS["invalid_url"] in text, True)

	@unittest_run_loop
	async def test_busy_url(self):
		resp = await self.client.post('/', data={"url": "http://example.org/", "user_url": "my_url"})
		self.assertEqual(resp.status, 200)
		resp = await self.client.post('/', data={"url": "http://example.org/", "user_url": "my_url"})
		self.assertEqual(resp.status, 200)
		text = await resp.text()
		self.assertEqual(ERRORS["busy_url"] in text, True)


