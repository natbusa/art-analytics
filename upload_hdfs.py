import os
import argparse

from hdfs import Config

class HdfsClient:
  def __init__(self, profile):
    self.client = Config().get_client(profile)

h = HdfsClient('hdfs')

# We can now upload the data
h.client.makedirs('/photos')

# write file
hdfs_path = h.client.upload('/photos/', 'sequencefiles/photos.hsf', overwrite=True)
