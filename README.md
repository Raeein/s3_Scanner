<p align="center">
   
Sandy Castle combines the best feature of Sandcastle and CloudEnum and sprinkles some new functionlity on top of them. 

The script takes a target's name (e.g. `reddit`) and iterates through a file of bucket name permutations, such as the ones below:

```
training
bucket
dev
attachments
photos
elasticsearch
[...]
```

## Getting started

```
git clone https://github.com/Raeein/sandycastle.git
cd sandycastle/
pip install -r requirments.txt
python sandcastle.py -t reddit
```

```
usage: sandcastle.py [-h] -t TARGET [-f FILE] [-o OUTPUT] [-th THREADS] [-v] [-s] [-oP]

optional arguments:
  -h, --help            show this help message and exit
  -t TARGET, --target TARGET
                        Select a target stem name (e.g. 'shopify')
  -f FILE, --file FILE  Select the wordlist file to use (default: bucket-names.txt)
  -o OUTPUT, --output OUTPUT
                        Select output file to use (default: output_'target'.txt)
  -th THREADS, --threads THREADS
                        Number of threads (default: 5)
  -v, --verbose         Prints out everything - use this flag for debugging preferably
  -s, --silent          Only prints out the found buckets
  -oP, --public         Only prints out the found public buckets

```

```
   _____                 __         ______           __  __        ___    ____ 
  / ___/____ _____  ____/ /_  __   / ____/___ ______/ /_/ /__     |__ \  / __ \
  \__ \/ __ `/ __ \/ __  / / / /  / /   / __ `/ ___/ __/ / _ \    __/ / / / / /
 ___/ / /_/ / / / / /_/ / /_/ /  / /___/ /_/ (__  ) /_/ /  __/   / __/_/ /_/ / 
/____/\__,_/_/ /_/\__,_/\__, /   \____/\__,_/____/\__/_/\___/   /____(_)____/  
                       /____/                                                  

    S3 bucket enumeration // release v2.0.0
```

### Status codes and testing

| Status code        | Definition           | Notes  |
| ------------- | ------------- | -----|
| 404      | Bucket Not Found | Not a target for analysis (hidden by default)|
| 403      | Access Denied      |   Potential target for analysis via the aws CLI |
| 200 | Publicly Accessible      |    Potential target for analysis via the aws CLI  |

### AWS CLI commands
Here's a quick reference of some useful AWS CLI commands:
* List Files: `aws s3 ls s3://bucket-name`
* Download Files: `aws s3 cp s3://bucket-name/<file> <destination>`
* Upload Files: `aws s3 cp/mv test-file.txt s3://bucket-name`
* Remove Files: `aws s3 rm s3://bucket-name/test-file.txt`

## Closing remarks
* Credits to sandcastle and cloud_enum for making this script possbile
* sandcastle: https://github.com/0xSearches/sandcastle
* cloud_enum: https://github.com/initstring/cloud_enum.git
