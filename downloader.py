from urllib2 import urlopen as download_file
from time import time as time_now
from urlparse import urlparse
import os
from os import path

class BaseDownload(object):
    def __init__(self, url, output_file):
        self.url = url
        self.output_file = output_file
        self.success = False
        self.block_size = 4096
        self.kbps = 0
        self.total_downloaded = 0
        self.file_size = 0
        self.last_time = 0
        
    def start(self):
        stream = download_file(self.url)
        meta = stream.info()
        self.file_size = int(meta.getheaders("Content-Length")[0])
        with self.output_file as f:
            while True:
                buffer = stream.read(self.block_size)
                if not buffer:
                    break
                f.write(buffer)
                downloaded = len(buffer)
                self.__calculate_metrics(downloaded)
            
    def __calculate_metrics(self, downloaded_length):
        diff = self.__get_time_diff()
        if diff:
            self.total_downloaded += downloaded_length
            
            speed_multiplier = 1.0 / diff
            bits_ps = downloaded_length * speed_multiplier
            kbytes_ps = bits_ps / float(8 * 1024)
            self.kbps = round(kbytes_ps,3)
        
    def __get_time_diff(self):
        now = time_now()
        if self.last_time:
            return now - self.last_time
        self.last_time = now

class DownloadToPath(BaseDownload):
    def __init__(self, url, output_path):
        if not path.isfile(output_path):
            output_file = open(output_path, 'ab')
            BaseDownload.__init__(self, url, output_file)
        else:
            raise Exception("Specified output file already exists. You must remove it first. '%s'" % path.abspath(output_path))

class DownloadToDirectory(DownloadToPath):
    '''
    Guesses the file name and downloads the file writing to the output directory
    '''
    def __init__(self, url, output_directory):
        up = urlparse(url)
        file_name = path.basename(up.path)
        file_path = path.join(output_directory, file_name)
        DownloadToPath.__init__(self, url, file_path)
        
class DownloadWithDirectory(DownloadToDirectory):
    '''
    Builds the file path for the file to be downloaded
    '''
    def __init__(self, url, output_directory, include_domain=True):
        up = urlparse(url)
        path = up.path
        path_parts = path.split("/")
        if include_domain:
            path_parts.insert(0, up.netloc)
        output_directory = self.build_path(output_directory, path_parts)
        DownloadToDirectory.__init__(self, url, output_directory)
            
    def build_path(self, base_path, path_parts):
        full_path = base_path
        for path in path_parts:
            full_path = path.join(full_path, path)
            os.makedirs(full_path)
        return full_path
        
class Download(DownloadToDirectory):
    def __init__(self, url, output_directory=""):
        DownloadToDirectory.__init__(self, url, output_directory)
            
        
