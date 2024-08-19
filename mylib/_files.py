import uuid
import hashlib
import warnings
import itertools as it
import functools as ft
from pathlib import Path

class FileObject:
    _window = 20

    def __init__(self, path):
        self.fp = path.open('rb')
        self.chunk = 2 ** self._window

    def close(self):
        self.fp.close()

    @ft.cached_property
    def checksum(self):
        csum = hashlib.blake2b()

        while True:
            data = self.fp.read(self.chunk)
            if not data:
                break
            csum.update(data)
        self.fp.seek(0)

        return csum.hexdigest()

class FileStream:
    def __init__(self, paths):
        self.paths = paths
        self.streams = []

    def __len__(self):
        return len(self.streams)

    def __iter__(self):
        for p in self.paths:
            stream = FileObject(p)
            self.streams.append(stream)
            yield stream

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        for s in self.streams:
            s.close()
        self.streams.clear()

class FileManager:
    def __init__(self, client, prefix, batch_size=20):
        self.client = client
        self.prefix = prefix
        self.batch_size = batch_size

        self.storage = set()
        self.vector_store_id = None

    def __bool__(self):
        return self.vector_store_id is not None

    def __iter__(self):
        if self:
            kwargs = {}
            while True:
                vs_files = self.client.beta.vector_stores.files.list(
                    vector_store_id=self.vector_store_id,
                    **kwargs,
                )
                for f in vs_files.data:
                    result = self.client.files.retrieve(f.id)
                    yield result.filename

                if not vs_files.has_more:
                    break
                kwargs['after'] = vs_files.after

    def __call__(self, paths):
        files = []
        self.test_and_setup()

        for p in self.ls(paths):
            with FileStream(p) as stream:
                for s in stream:
                    if s.checksum not in self.storage:
                        files.append(s.fp)
                        self.storage.add(s.checksum)
                if files:
                    self.put(files)
                    files.clear()

        return '\n'.join(self)

    def test_and_setup(self):
        if self:
            msg = f'Vector store already exists ({self.vector_store_id})'
            warnings.warn(msg)
        else:
            name = f'{self.prefix}{uuid.uuid4()}'
            vector_store = self.client.beta.vector_stores.create(
	        name=name,
            )
            self.vector_store_id = vector_store.id

    def ls(self, paths):
        left = 0
        while left < len(paths):
            right = left + self.batch_size
            yield list(map(Path, it.islice(paths, left, right)))
            left = right

    def put(self, files):
        batch = self.client.beta.vector_stores.file_batches.upload_and_poll(
            vector_store_id=self.vector_store_id,
            files=files,
        )
        if batch.file_counts.completed != len(files):
            err = f'Error uploading documents: {batch.file_counts}'
            raise InterruptedError(err)
