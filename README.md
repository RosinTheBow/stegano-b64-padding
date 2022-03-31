# stegano-b64-padding
Encoding and retrieving message hidden in the padding of base64 encoding 

This script encodes and decodes characters to/from the base64 word-by-word padding of a text.

First, there is the encode mode: 
```
usage: stegano-b64-padding.py encode [-h] [-o FILE] [-v]
                                     (-p FILE | -P plaintext)
                                     (-s FILE | -S secret)

optional arguments:
  -h, --help    show this help message and exit
  -o FILE       File to write the output to. Default: stdout
  -v            Increase verbosity
  -p FILE       Plaintext in which the secret will be encoded - FILE
  -P plaintext  Plaintext in which the secret will be encoded - console
  -s FILE       Secret to be encoded - FILE
  -S secret     Secret to be encoded - console
```
Example:
```
$ ./stegano-b64-padding.py encode -p carrier_file.txt -S secret_message -o encoded.txt 
```

Then, there is the decode mode:
```
usage: stegano-b64-padding.py decode [-h] -p FILE [-o FILE] [-n] [-v]

optional arguments:
  -h, --help  show this help message and exit
  -p FILE     Encoded file to extract the secret from
  -o FILE     File to write the output to. Default: stdout
  -n          Do not show carrier text
  -v          Increase verbosity
```
Example:
```
$ ./stegano-b64-padding.py decode -n -p encoded.txt 
```
