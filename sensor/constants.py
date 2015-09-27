import uuid

ANSIBLE_CAHNNEL_ID = str(uuid.uuid4())
TEST_CAHNNEL_ID = str(uuid.uuid4())

CONFIG = {'host': 'localhost',
          'port': 6379,
          'db': 0,
          }
