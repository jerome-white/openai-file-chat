import time
from argparse imAAport ArgumentParser

from scipy import constants
from openai import OpenAI

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
        age = (other - self.now) * constants.hour
        return age < self.limit

if __name__ == '__main__':
    arguments = ArgumentParser()
    arguments.add_argument('--max-age-hours', type=int)
    args = arguments.parse_args()

    client = OpenAI()
    if args.max_age_hours is None:
        acheck = NoAgeCheck()
    else:
        acheck = HourAgeCheck(args.max_age_hours)

    while True:
        assistants = client.beta.assistants.list()
        for a in assistants:
            if a.created_at in acheck:
                continue
            if a.tool_resources.file_search is not None:
                for i in a.tool_resources.file_search.vector_store_ids:
                    Logger.warning(f'{a.id} {i}')
                    vsm = VectorStoreManager(i)
                    vsm.cleanup()
            client.beta.assistants.delete(a.id)

        if not assistants.has_more:
            break
