"""
 This file is part of Python-Downloader.

 Python-Downloader is free software: you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation, either version 3 of the License, or
 (at your option) any later version.

 Python-Downloader is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public License for more details.

 You should have received a copy of the GNU General Public License
 along with Python-Downloader.  If not, see <http://www.gnu.org/licenses/>.
"""

import unittest
import os
from SimpleHTTPServer import SimpleHTTPRequestHandler
from SocketServer import TCPServer
from threading import Thread
from downloader import Download, DownloadToPath, DownloadToDirectory, DownloadWithDirectory
from hashlib import md5

PORT = 8081
TEST_DIR = "test_dir"
TEST_FILE = "f623265e8ac129dd7f0b75a8d06857dd"
URL = "http://localhost:%d/%s/" % (PORT, TEST_DIR)

class setUpAll(unittest.TestCase):
    def setUp(self):
        handler = SimpleHTTPRequestHandler
        httpd = TCPServer(("", PORT), handler)
        httpd.allow_reuse_address = True
        self.httpd_thread = Thread(target=httpd.serve_forever)
        self.httpd_thread.setDaemon(True)
        self.httpd_thread.start()
        
    def md5sum(self, path):
        f = open(path, 'r')
        data = f.read()
        sum = md5(data)
        return sum.hexdigest()

class TestDownload(setUpAll):
    def test_download_file(self):
        url = URL + TEST_FILE
        dl = Download(url)
        dl.start()
        
        # test it created the file
        self.assertTrue(os.path.isfile(TEST_FILE))
        
        # test it's the same file
        sum = self.md5sum(TEST_FILE)
        self.assertEqual(sum, TEST_FILE)
        
        # test metrics
        self.assertTrue(dl.kbps > 0)
        
    def tearDown(self):
        os.unlink(TEST_FILE)
        
class TestDownloadToFilePath(setUpAll):
    out_file_path = "testoutput"
    def test_download_file(self):
        url = URL + TEST_FILE
        dl = DownloadToPath(url, self.out_file_path)
        dl.start()
        
        # test it created the file
        self.assertTrue(os.path.isfile(self.out_file_path))
        
        # test it's the same file
        sum = self.md5sum(self.out_file_path)
        self.assertEqual(sum, self.out_file_path)
        
        # test metrics
        self.assertTrue(dl.kbps > 0)
        
    def tearDown(self):
        os.unlink(self.out_file_path)

if __name__ == "__main__":
    unittest.main()
