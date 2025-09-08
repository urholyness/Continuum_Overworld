
class DownloaderAgent:
    """Agent based on Downloader from ..\Nyxion\env\Lib\site-packages\pip\_internal\network\download.py"""
    
    def __init__(self):
        self.name = "DownloaderAgent"
        self.category = "utility"
        self.status = "active"
    
    def process(self, data):
        """Process data using the original pattern logic"""
                assert resume_retries >= 0, 'Number of max resume retries must be bigger or equal to zero'
        self._session = session
        self._progress_bar = progress_bar
        self._resume_retries = resume_retries
    def __call__(self, link: Link, location: str) -> Tuple[str, str]:
        """Download the file given by link into location."""
        resp = _http_get_download(self._session, link)
        total_length = _get_http_response_size(resp)
        content_type = resp.headers.get('Content-Type', '')
        filename = _get_http_response_filename(resp, link)
        filepath = os.path.join(location, filename)
        with open(filepath, 'wb') as content_file:
            bytes_received = self._process_response(resp, link, content_file, 0, total_length)
            if total_length and bytes_received < total_length:
                self._attempt_resume(resp, link, content_file, total_length, bytes_received)
        return (filepath, content_type)
    def _process_response(self, resp: Response, link: Link, content_file: BinaryIO, bytes_received: int, total_length: Optional[int]) -> int:
        """Process the response and write the chunks to the file."""
        chunks = _prepare_download(resp, link, self._progress_bar, total_length, range_start=bytes_received)
        return self._write_chunks_to_file(chunks, content_file, allow_partial=bool(total_length))
    def _write_chunks_to_file(self, chunks: Iterable[bytes], content_file: BinaryIO, *, allow_partial: bool) -> int:
        """Write the chunks to the file and return the number of bytes received."""
        bytes_received = 0
        try:
            for chunk in chunks:
                bytes_received += len(chunk)
                content_file.write(chunk)
        except ReadTimeoutError as e:
            if not allow_partial:
                raise e
            logger.warning('Connection timed out while downloading.')
        return bytes_received
    def _attempt_resume(self, resp: Response, link: Link, content_file: BinaryIO, total_length: Optional[int], bytes_received: int) -> None:
        """Attempt to resume the download if connection was dropped."""
        etag_or_last_modified = _get_http_response_etag_or_last_modified(resp)
        attempts_left = self._resume_retries
        while total_length and attempts_left and (bytes_received < total_length):
            attempts_left -= 1
            logger.warning('Attempting to resume incomplete download (%s/%s, attempt %d)', format_size(bytes_received), format_size(total_length), self._resume_retries - attempts_left)
            try:
                resume_resp = _http_get_download(self._session, link, range_start=bytes_received, if_range=etag_or_last_modified)
                must_restart = resume_resp.status_code != HTTPStatus.PARTIAL_CONTENT
                if must_restart:
                    bytes_received, total_length, etag_or_last_modified = self._reset_download_state(resume_resp, content_file)
                bytes_received += self._process_response(resume_resp, link, content_file, bytes_received, total_length)
            except (ConnectionError, ReadTimeoutError, OSError):
                continue
        if total_length and bytes_received < total_length:
            os.remove(content_file.name)
            raise IncompleteDownloadError(link, bytes_received, total_length, retries=self._resume_retries)
    def _reset_download_state(self, resp: Response, content_file: BinaryIO) -> Tuple[int, Optional[int], Optional[str]]:
        """Reset the download state to restart downloading from the beginning."""
        content_file.seek(0)
        content_file.truncate()
        bytes_received = 0
        total_length = _get_http_response_size(resp)
        etag_or_last_modified = _get_http_response_etag_or_last_modified(resp)
        return (bytes_received, total_length, etag_or_last_modified)
        
    def run(self, *args, **kwargs):
        """Main execution method"""
        return self.process(*args, **kwargs)
