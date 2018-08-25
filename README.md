# `filewatcher-aws-trigger`

Experimental File Watcher program to trigger AWS Lambda.

Triggers AWS Lambda based on given function name with a known trigger file path,
and using default AWS credentials based on `boto3`, such as placing `config` and
`credentials` into `~/.aws/`.

Submits payload of the given JSON form in byte format:

```json
{
  "path": "<triggered file path: string>"
}
```

## Usage

### Docker

Visit <https://hub.docker.com/r/guangie88/filewatch-aws-trigger/> to check out
the pre-built Docker images to immediately use the application.

As an example:

```bash
docker run --rm -it guangie88/filewatch-aws-trigger:python-3.7 -h
```

This should present the application help screen for more usage infomation.

For a quick and easy usage example:

```bash
docker run --rm -it -v ~/.aws:/root/.aws -v ${PWD}:/app \
    guangie88/filewatch-aws-trigger:python-3.7 \
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

### Native

If you prefer running the application natively using Python 3 without Docker,
you can simply run the following to get the application running like in the
Docker example above:

```bash
python3 -m pip install --user -r requirements.txt
./app.py -p . -f "*.jpg,*.png" -n test-trigger
```

Note that you will need Python 3.6 to run the script properly.
