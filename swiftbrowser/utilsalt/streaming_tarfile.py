import tarfile

from django.utils.six.moves import cStringIO as StringIO

from swiftclient import client


class FileStream(object):
    """File stream for streaming reponses

    This buffer intended for use as an argument to StreamingHTTPResponse
    and also as a file for TarFile to write into.

    Files are read in by chunks and written to this buffer through TarFile.
    When there is content to be read from the buffer, it is taken up by
    StreamingHTTPResponse and the buffer is cleared to prevent storing large
    chunks of data in memory.
    """
    def __init__(self):
        self.buffer = StringIO()
        self.offset = 0

    def write(self, s):
        """Write ``s`` to the buffer and adjust the offset."""
        self.buffer.write(s)
        self.offset += len(s)

    def tell(self):
        """Return the current position of the buffer."""
        return self.offset

    def close(self):
        """Close the buffer."""
        self.buffer.close()

    def pop(self):
        """Return the current contents of the buffer then clear it."""
        s = self.buffer.getvalue()
        self.buffer.close()

        self.buffer = StringIO()

        return s


class StreamingTarFile(object):
    """ A streaming TarFile object for StreamingHTTPReponse.

    For arguments: takes an ```out_filename``` (the filename to write out to)
    and a list of ```files``` from a request.

    Handles building TarInfo objects for each file and also writing chunks of
    files out to a file object (FileStream).
    """

    def __init__(
            self, out_filename, files, storage_url, auth_token, container):
        """Set constants, output filename and list of files to tarball."""
        self.MODE = 0644
        self.BLOCK_SIZE = 4096
        self.out_filename = out_filename
        self.files = files
        self.storage_url = storage_url
        self.auth_token = auth_token
        self.container = container

    def build_tar_info(self, meta, name):
        """Build TarInfo object to represent one file in tarball."""
        tar_info = tarfile.TarInfo(name)
        tar_info.mode = self.MODE
        tar_info.size = int(meta["content-length"])
        tar_info.mtime = float(meta["x-timestamp"])

        return tar_info

    def stream_build_tar(self, streaming_fp):
        """Build tarball by writing it's contents out to streaming_fp."""
        tar = tarfile.TarFile.open(self.out_filename, 'w|gz', streaming_fp)

        for name in self.files:

            yield
            meta, content = client.get_object(
                self.storage_url, self.auth_token, self.container, name)

            tar_info = self.build_tar_info(meta, name)
            tar.addfile(tar_info)

            tar.fileobj.write(content)

            # Write nulls at the end of the file so that the total amount
            # written to the stream is a multiple of BLOCKSIZE
            blocks, remainder = divmod(tar_info.size, tarfile.BLOCKSIZE)
            if remainder > 0:
                tar.fileobj.write(tarfile.NUL * (tarfile.BLOCKSIZE - remainder))

            blocks += 1

            tar.offset += blocks * tarfile.BLOCKSIZE

        tar.close()

        yield

    def generate(self):
        """Generate FileStream object to stream via StreamingHttpResponse."""
        streaming_fp = FileStream()
        for i in self.stream_build_tar(streaming_fp):
            s = streaming_fp.pop()

            if len(s) > 0:
                yield(s)
