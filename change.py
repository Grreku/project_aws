import boto3
import skimage
import skimage.io
import skimage.transform
import os
import datetime

sqs = boto3.resource("sqs", region_name='us-west-2')
queue = sqs.get_queue_by_name(QueueName="projekt-psoir-queue")
s3 = boto3.resource('s3')
simpledb = boto3.client("sdb")

while True:
    message_list = queue.receive_messages(MaxNumberOfMessages=10, VisibilityTimeout=30)
    for message in message_list:
        image_name = message.body
        image = s3.meta.client.download_file("projekt-psoir1", "uploads/{0}".format(image_name), "temp_{0}".format(image_name))
        image_to_transform = skimage.io.imread("temp_{0}".format(image_name))
        transformed_image = skimage.transform.rotate(image_to_transform, 180)
        skimage.io.imsave("changed_{0}".format(image_name), transformed_image)
        s3.meta.client.upload_file("changed_{0}".format(image_name), "projekt-psoir1", "changed/{0}".format(image_name))
        simpledb.put_attributes(DomainName="PsoirSimpleDB", ItemName="ChangedImage",
        Attributes=[{"Name":"Name", "Value":"changed_{0}".format(image_name), "Replace":True}, {"Name":"Time", "Value":str(datetime.datetime.now()), "Replace":True}])

        message.delete()
        os.remove("temp_{0}".format(image_name))
        os.remove("changed_{0}".format(image_name))
