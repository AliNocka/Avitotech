import aioredis


class LocalDatabase:
	"""
	Имплементация локальной базы данных (NOTE: предполагается для использования в тестах)
	Реализует функционал redis из aioredis
	"""

	def __init__(self):
		self._data = {}

	async def get(self, key):
		return self._data.get(key)

	async def set(self, key, value):
		self._data[key] = str.encode(value)

	async def incr(self, key):
		value = int(self._data.get(key, b"0").decode("utf-8"))
		value += 1
		self._data[key] = str.encode(str(value))
		return value

	def close(self):
		pass

	async def wait_closed(self):
		pass


class DBFactory:
	"""
	Фабрика для получения различных имплементаций баз данных
	"""

	@staticmethod
	async def get_db(dbname, config):
		if dbname == "redis":
			redis = await aioredis.create_redis_pool("redis://{}:{}".format(config["redis_host"], config["redis_port"]),\
                                                     db=config["db"], password=config["redis_password"])
			return redis
		elif dbname == "local":
			return LocalDatabase()
		else:
			raise ValueError("Incorrect database name")
