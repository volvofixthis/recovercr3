import os

class MultiFileReader:
    def __init__(self, filenames):
        self.filenames = filenames
        self.file_sizes = [os.path.getsize(f) for f in filenames]
        self.total_size = sum(self.file_sizes)
        self.current_index = 0  # which file we are in
        self.current_file = None
        self.pos = 0  # global position
        self._open_file(self.current_index)

    def _open_file(self, index):
        if self.current_file:
            self.current_file.close()
        self.current_file = open(self.filenames[index], 'rb')
        self.current_index = index

    def _seek_to_pos(self, global_pos):
        if global_pos < 0:
            raise ValueError("Negative seek position")
        if global_pos > self.total_size:
            global_pos = self.total_size

        self.pos = global_pos
        # Find which file the position falls into
        accumulated = 0
        for i, size in enumerate(self.file_sizes):
            if accumulated + size > global_pos:
                offset_in_file = global_pos - accumulated
                self._open_file(i)
                self.current_file.seek(offset_in_file)
                return
            accumulated += size
        # If here, we're at or beyond the end
        self._open_file(len(self.filenames) - 1)
        self.current_file.seek(self.file_sizes[-1])

    def read(self, size=-1):
        if size == 0 or self.pos >= self.total_size:
            return b''

        if size < 0:
            size = self.total_size - self.pos

        result = bytearray()
        while size > 0 and self.pos < self.total_size:
            bytes_left_in_file = self.file_sizes[self.current_index] - self.current_file.tell()
            to_read = min(size, bytes_left_in_file)
            chunk = self.current_file.read(to_read)
            if not chunk:
                if self.current_index + 1 >= len(self.filenames):
                    break
                self._open_file(self.current_index + 1)
                continue
            result.extend(chunk)
            self.pos += len(chunk)
            size -= len(chunk)
        return bytes(result)

    def seek(self, offset, whence=os.SEEK_SET):
        if whence == os.SEEK_SET:
            target = offset
        elif whence == os.SEEK_CUR:
            target = self.pos + offset
        elif whence == os.SEEK_END:
            target = self.total_size + offset
        else:
            raise ValueError("Invalid whence value")
        self._seek_to_pos(target)

    def seekable(self):
        return True

    def tell(self):
        return self.pos

    def close(self):
        if self.current_file:
            self.current_file.close()
            self.current_file = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
