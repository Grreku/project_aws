from flask import Flask, request, render_template
import boto3
import os
import datetime

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/done')
def done():
    return render_template('done.html')

@app.route('/choose')
def modify():
    client = boto3.client('s3')
    response = client.list_objects_v2(
    Bucket = 'projekt-psoir1',
    Prefix = 'uploads/'
    )
    image_list = []
    for image in response["Contents"]:
       image_list.append(image["Key"].split('/')[1])
    return render_template('choose.html', image_list=image_list)


@app.route('/queue', methods=["POST"])
def queue():
    image_list = request.form.getlist("uploads")
    sqs = boto3.resource("sqs")
    queue = sqs.get_queue_by_name(QueueName="projekt-psoir-queue")
    simpledb = boto3.client("sdb")
    for image_name in image_list:
        queue.send_message(MessageBody="{0}".format(image_name))
        simpledb.put_attributes(DomainName="PsoirSimpleDB", ItemName="Image",
        Attributes=[{"Name":"Name", "Value":image_name, "Replace":True}])

    return render_template("sent.html")


if __name__ == '__main__':
    app.run()

