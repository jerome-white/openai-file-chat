import time
import json
from pathlib import Path
from argparse import ArgumentParser

from scipy import constants
from openai import OpenAI, NotFoundError

from mylib import Logger, VectorStoreManager

class AgeCheck:
    def __init__(self):
        self.now = time.time()

    def __contains__(self, other):
        raise NotImplementedError()

class NoAgeCheck(AgeCheck):
    def	__contains__(self, other):
        return False

class HourAgeCheck(AgeCheck):
    def	__init__(self, hours):
        super().__init__()
        self.limit = hours

    def __contains__(self, other):
        age = (self.now - other) / constants.hour
        return age < self.limit

def assistants(client, age_limit, name):
    kwargs = {}
    while True:
        page = client.beta.assistants.list(**kwargs)
        for a in page:
            if a.name == name and a.created_at not in age_limit:
                yield a

        if not page.has_more:
            break
        kwargs['after'] = page.last_id

if __name__ == '__main__':
    arguments = ArgumentParser()
    arguments.add_argument('--config', type=Path)
    arguments.add_argument('--max-age-hours', type=int)
    args = arguments.parse_args()

    config = (json
              .loads(args.config.read_text())
              .get('openai'))
    if args.max_age_hours is None:
        acheck = NoAgeCheck()
    else:
        acheck = HourAgeCheck(args.max_age_hours)
    name = config['assistant_name']
    client = OpenAI(api_key=config['api_key'])

    remove = []
    for a in assistants(client, acheck, name):
        Logger.critical(a.id)
        if a.tool_resources.file_search is not None:
            for i in a.tool_resources.file_search.vector_store_ids:
                Logger.warning(f'{a.id} {i}')
                vsm = VectorStoreManager(client, i)
                vsm.cleanup()
        remove.append(a.id)

    for a in remove:
        try:
            client.beta.assistants.delete(a)
        except NotFoundError:
            Logger.error(a)
