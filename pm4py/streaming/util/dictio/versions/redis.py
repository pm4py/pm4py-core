from enum import Enum
from threading import Lock
from typing import Optional, Dict, Any

from pm4py.util import exec_utils


class Parameters(Enum):
    HOSTNAME = "hostname"
    PORT = "port"
    DICT_ID = "dict_id"


class ThreadSafeRedisDict(dict):
    def __init__(self, redis_connection, *args, **kw):
        super(ThreadSafeRedisDict, self).__init__(*args, **kw)
        self.redis_connection = redis_connection
        self.lock = Lock()

    def __setitem__(self, key, value):
        # TODO: what should happen to the order if
        #       the key is already in the dict
        self.lock.acquire()
        self.redis_connection[key] = value
        super(ThreadSafeRedisDict, self).__setitem__(key, value)
        self.lock.release()

    def __iter__(self):
        self.lock.acquire()
        ret = iter(list(self.redis_connection.keys()))
        self.lock.release()
        return ret

    def keys(self):
        self.lock.acquire()
        ret = list(self.redis_connection.keys())
        self.lock.release()
        return ret

    def values(self):
        self.lock.acquire()
        ret = self.redis_connection.values()
        self.lock.release()
        return ret

    def itervalues(self):
        self.lock.acquire()
        ret = self.redis_connection.itervalues()
        self.lock.release()
        return ret

    def flushdb(self):
        self.lock.acquire()
        self.redis_connection.flushdb()
        self.lock.release()

    def flushall(self):
        self.lock.acquire()
        self.redis_connection.flushall()
        self.lock.release()


# typing not applied, since redis is not installed by default
# anyhow, the type of the returned "r" is redis.redis.Redis
def apply(parameters: Optional[Dict[Any, Any]] = None):
    """
    Create a Python dictionary supported by a Redis database

    Parameters
    --------------
    parameters
        Parameters of the algorithm, including:
        - Parameters.HOSTNAME => hostname of the connection to Redis (default: 127.0.0.1)
        - Parameters.PORT => port of the connection to Redis (default: 6379)
        - Parameters.DICT_ID => integer identifier of the specific dictionary in Redis (default: 0)

    Returns
    --------------
    r
        Redis (Python-like) dictionary
    """
    if parameters is None:
        parameters = {}

    import redis

    hostname = exec_utils.get_param_value(Parameters.HOSTNAME, parameters, "127.0.0.1")
    port = exec_utils.get_param_value(Parameters.PORT, parameters, 6379)
    dict_id = exec_utils.get_param_value(Parameters.DICT_ID, parameters, 0)

    r = redis.StrictRedis(host=hostname, port=port, db=dict_id, decode_responses=True)

    return ThreadSafeRedisDict(r)
