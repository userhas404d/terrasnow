"""S3 operations handler."""

import logging
import pathlib

import boto3

"""
1. receive file name and loc as well as sys_id of category item
2. Get template name from file name (remove suffix)
3. confirm target bucket exists and is accessible, False if not
4. upload file to target_bucket
5. return uri of file
"""

s3 = boto3.client('s3')


class Handler(object):
    """S3 Handler class."""

    def __init__(self, file_name, sys_id, loc_file_path, target_bucket):
        """Initialize."""
        self.file_name = file_name
        self.sys_id = sys_id
        self.target_bucket = target_bucket
        self.upload_file_name = self.get_upload_file_name(file_name)
        self.loc_file_path = loc_file_path
        self.obj_uri = self.get_obj_uri()

    def local_file_check(self):
        """Check if file exists on local disk."""
        if self.loc_file_path:
            check_file = pathlib.Path(self.loc_file_path)
            if check_file.is_file():
                logging.info('File found on local disk.')
                return True
            else:
                logging.error('File not found.')
                return False
        else:
            logging.info('file path not provided.')
            return False

    def check_bucket(self):
        """Confirm bucket exists."""
        response = s3.list_buckets()
        # reference: https://stackoverflow.com/questions/3897499
        if not any(d['Name'] == self.target_bucket
                   for d in response['Buckets']):
            logging.error('Target bucket: {} not found.'.format(
                self.target_bucket))
            return False
        else:
            logging.info('Target bucket exists.')
            return True

    def s3_file_check(self):
        """Check if file exists in bucket."""
        response = s3.list_objects(Bucket=self.target_bucket)
        try:
            if not any(d['Key'] == self.upload_file_name
                       for d in response['Contents']):
                logging.info('file: {} not in bucket.'.format(
                             self.upload_file_name))
                return True
            else:
                logging.info('file: {} in bucket.'.format(
                    self.upload_file_name))
                return False
        except KeyError as e:
            logging.info('Bucket is empty.')
            return True

    def get_obj_uri(self):
        """Create object URI."""
        # https://stackoverflow.com/questions/33809592
        if (not self.sys_id and
                self.check_bucket() and
                self.local_file_check()):
            return ('s3::https://s3.amazonaws.com/{0}/{1}'.format(
                    self.target_bucket, self.upload_file_name))
        elif(self.file_name and self.target_bucket):
            return None
        else:
            logging.error('URL creation failed.')
            print('ERROR: URL creation failed.')

    def get_upload_file_name(self, file_name):
        """Return the name of the file to upload."""
        if self.sys_id and self.file_name:
            return (self.sys_id + '-' + self.file_name).replace(" ", "")
        else:
            return file_name.replace(" ", "")

    def upload_file(self):
        """Upload file."""
        if (self.check_bucket() and
                self.s3_file_check() and
                self.local_file_check()):
            s3.upload_file(self.loc_file_path, self.target_bucket,
                           self.upload_file_name)
            return True
        else:
            logging.error('File upload failed.')
            return False

    def upload_file_override(self):
        """Upload file even if its already in the bucket."""
        if self.check_bucket() and self.local_file_check():
            s3.upload_file(self.loc_file_path, self.target_bucket,
                           self.upload_file_name)
            return True
        else:
            logging.error('File overwrite failed.')
            return False

    def download_obj(self):
        """Download an object provieded its uri."""
        if not self.s3_file_check():
            logging.info('Retrieving object: {}'.format(self.file_name))
            with open(self.loc_file_path, 'wb') as data:
                s3.download_fileobj(self.target_bucket, self.file_name, data)
        else:
            logging.error('Object not in bucket.')

    def delete_obj(self):
        """Delete an object provided its bucketname and key."""
        if not self.s3_file_check():
            s3.delete_object(Bucket=self.target_bucket,
                             Key=self.upload_file_name)
        else:
            logging.error(self.upload_file_name + ' is not in bucket '
                          + self.target_bucket)
