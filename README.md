# `filewatch-trigger`

[![Build Status](https://travis-ci.org/guangie88/filewatch-trigger.svg?branch=master)](https://travis-ci.org/guangie88/filewatch-trigger)

Experimental File Watcher program to trigger any of the below actions:

- AWS Lambda function
- Shell template command

## Docker Usage

Visit <https://hub.docker.com/r/guangie88/filewatch-trigger/> to check out the
pre-built Docker images to immediately use the application.

As an example:

```bash
docker run --rm -it guangie88/filewatch-trigger:python-3.7 -h
```

This should present the application help screen for more usage infomation.

### AWS Lambda function

Triggers AWS Lambda based on given function name with a known trigger file path,
and using default AWS credentials based on `boto3`, such as placing `config` and
`credentials` into `~/.aws/`.

Submits payload of the given JSON form in byte format:

```json
{
  "path": "<triggered file path: string>"
}
```

For a quick and easy usage example:

```bash
docker run --rm -it -v ~/.aws:/root/.aws -v ${PWD}:/app \
    guangie88/filewatch-trigger:python-3.7 \
    aws-lambda \
    -p . \
    -f "*.jpg,*.png" \
    -n test-trigger
```

The above command mounts both your current host AWS credentials and current
directory, and runs the application watching the current host directory
recursively for newly created files ending with `.jpg` and `.png`. The
application will trigger the AWS Lambda function `test-trigger` with the given
absolute path.

As such, you will need to have a test AWS Lambda function named `test-trigger`,
which could look something like this:

```python
def lambda_handler(event, context):
    return 'Path is {}'.format(event['path'])
```

### Shell template command

For a quick and easy usage example:

```bash
docker run --rm -it -v ~/.aws:/root/.aws -v ${PWD}:/app \
    guangie88/filewatch-trigger:python-3.7 \
    cmd \
    -p . \
    -f "*.jpg,*.png" \
    -c "echo \"(File: {0}, Event: {1})\""
```

The above command runs the application watching the current host directory
recursively for newly created files ending with `.jpg` and `.png`, and runs
the `echo` command with the actual path substituted into `{0}` and event name
into `{1}`.

An example echo output is as follow: `(File: /app/a.png, Event: created)`.

## Running Native

If you prefer running the application natively using Python 3 without Docker,
you can simply run the following to get the application running like in the
Docker example above:

```bash
python3 -m pip install --user -r requirements.txt
./app.py -p . -f "*.jpg,*.png" -n test-trigger
```

Note that you will need Python 3.6 to run the script properly.
