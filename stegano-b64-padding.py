#!/usr/bin/env python3
# Base64 Steganography - hiding a secret in the padding of the Base64 encoding
# 
# Author: RosinTheBow
# 
# When converting strings from ASCII to Base64 it may be necessary to pad the 
# input with zeros. When decoding, the padding is ignored. Thus, the encoding
# process could be altered to pad with chosen bits instead of zeros. By 
# choosing these bits, one can hide information in a set of Base64-encoded
# strings
#
# This script performs both the encoding and the secret extraction explained 
# above. The encoding takes an ASCII text (or carrier) and encodes each word
# in Base64, then modifies the last character according to the chosen custom
# padding. The decoding process looks at the padding of each strings and 
# reconstructs the secret.
#

import re, argparse, pathlib, sys
from base64 import b64encode, b64decode

# Dictionary containing the Base64 characters
dict = [chr(x) for x in range(65,91)] + [chr(x) for x in range(97,123)] + [chr(x) for x in range(48,58)] + ['+','/']

def encode_word(word, secret):
    """Encode 2 or 4 bits of secret inside base64 encoded word

    Arguments:
    word (str)           -- Base64 encoded word serving as carrier
    secret (str)         -- 2-bit or 4-bit secret to hide

    Output:
    encoded_string (str) -- Re-encoded base64 string with secret
    """
    first_equal = word.index('=')
    to_modify = word[first_equal-1]
    delta = int(secret, 2)
    encoded_char = dict[dict.index(to_modify) + delta]
    encoded_string = word[:first_equal-1] + encoded_char + (len(word)-first_equal) * '='
    return encoded_string

def decode_word(word):
    """Extract secret bits from Base64 encoded word

    Arguments:
    word (str)       -- Base64 encoded string with hidden secret

    Output:
    secret (str)     -- 2-bit or 4-bit secret extracted from word
    ascii_word (str) -- the decoded base64 word
    """
    first_equal = word.index('=')
    encoded_char = word[first_equal-1]
    base = b64encode(b64decode(word))
    base_char = chr(base[first_equal-1])
    secret_index = dict.index(encoded_char) - dict.index(base_char)
    secret = "{0:b}".format(secret_index).zfill(2*word.count('='))
    return secret
    
def count_equals(word_list):
    """Returns the number of bits that can be hidden inside a text

    Arguments:
    word_list (str[]) -- List of Base64 strings 

    Output:
    count (int)       -- Number of '=' in the list times 2
    """
    equals = 0
    for word in word_list:
        equals += word.count('=')
    count = 2*equals
    return count

def encode(text, secret, verbose=False):
    """Encodes a secret in a base64 word list, from a text string

    Arguments:
    text (str)           -- ascii text serving as a carrier
    secret (str)         -- secret ascii text to encode of max length 2^16 words
    verbose (bool)       -- verbosity toggle

    Output:
    encoded_list (str[]) -- base64 list of words with the secret encoded within 
    """
    words = text.split(' ')
    words_b64 = [b64encode((word+" ").encode('ascii')).decode('ascii') for word in words]
    secret_max_length = count_equals(words_b64)
    if verbose: print('[*] Number of words: %d' % len(words))
    if verbose: print('[*] Maximum length of the secret: %d' % ((secret_max_length-16)//7))
    if verbose: print('[*] Length of the secret: %d' % len(secret))
    if 7*len(secret)+16 > secret_max_length:
        raise ValueError('[ERROR] The text size is too small for the secret. Please add more text.')
    if verbose: print('[*] Text size OK')
    bin_secret = bin(len(secret))[2:].zfill(16)
    for char in secret:
        bin_secret += bin(ord(char))[2:].zfill(7)
    bin_secret = bin_secret + (secret_max_length - len(bin_secret)) * '0'
    encoded_list = []
    for word in words_b64:
        equals = word.count('=')
        if equals > 0:
            encoded_list.append(encode_word(word, bin_secret[:2*equals]))
            bin_secret = bin_secret[2*equals:]
        else:
            encoded_list.append(word)
    return encoded_list

def decode(encoded_list, verbose=False):
    """Assemble the secret parts from each decoded base64 keyword

    Arguments:
    encoded_list (str[]) -- base64 list of encoded words containing the secret
    verbose (bool)       -- verbosity toggle

    Output:
    secret (str)         -- the secret extracted in ascii encoding
    """
    bin_secret = ''
    decoded_string = ''
    for word in encoded_list:
        if word.count('=') > 0:
            bin_secret += decode_word(word)
        decoded_string += b64decode(word).decode('ascii')
    secret_length = int(bin_secret[:16], 2)
    bin_secret = bin_secret[16:]
    binary_letters = re.findall('.{7}', bin_secret)[:secret_length]
    secret = ''.join(chr(int(letter, 2)) for letter in binary_letters)
    return secret, decoded_string

if __name__ == '__main__':

    parser = argparse.ArgumentParser(add_help = True, description = "Encodes and decodes secret text inside Base64 encoding")
    subparsers = parser.add_subparsers(title='modes of operation', description='Encode or Decode')

    encoder = subparsers.add_parser('encode', help='encodes secret in plaintext')
    encoder.add_argument('-o', metavar='FILE', help='File to write the output to. Default: stdout', type=pathlib.Path)
    encoder.add_argument('-v', help='Increase verbosity', action='store_true')
    decoder = subparsers.add_parser('decode', help='decodes secret from encoded list')
    decoder.add_argument('-p', metavar='FILE', help='Encoded file to extract the secret from', type=pathlib.Path, required=True)
    decoder.add_argument('-o', metavar='FILE', help='File to write the output to. Default: stdout', type=pathlib.Path)
    decoder.add_argument('-n', help='Do not show carrier text', action='store_true')
    decoder.add_argument('-v', help='Increase verbosity', action='store_true')
    
    encoder_plain = encoder.add_mutually_exclusive_group(required=True)
    encoder_secret = encoder.add_mutually_exclusive_group(required=True)
 
    encoder_plain.add_argument('-p', metavar='FILE', help='Plaintext in which the secret will be encoded - FILE', type=pathlib.Path)
    encoder_plain.add_argument('-P', metavar='plaintext', help='Plaintext in which the secret will be encoded - console', type=ascii)
    encoder_secret.add_argument('-s', metavar='FILE', help='Secret to be encoded - FILE', type=pathlib.Path)
    encoder_secret.add_argument('-S', metavar='secret', help='Secret to be encoded - console', type=ascii)

    if len(sys.argv)==1:
        parser.print_help()
        sys.exit(1)
    elif len(sys.argv)==2:
        if sys.argv[1]=='encode':
            encoder.print_help()
        elif sys.argv[1]=='decode':
            decoder.print_help()
        sys.exit(1)

    options = parser.parse_args()
    
    verbose = options.v

    if sys.argv[1] == 'encode':
        if verbose: print('[*] Encode mode chosen')
        if not options.p == None:
            try:
                if verbose: print('[*] Reading plaintext from file ...')
                f1 = open(options.p, 'r')
                plain = f1.read()
                f1.close()
            except OSError as e:
                print('[ERROR] Could not open file: %s ... Exiting' % options.p)
                sys.exit(0)
        else:
            if verbose: print('[*] Reading plaintext from console input ...')
            plain = options.P[1:-1]
        if verbose: print('[*] DONE')
        if not options.s == None:
            try:
                if verbose: print('[*] Reading secret from file ...')
                f1 = open(options.s, 'r')
                secret = f1.read()
                f1.close()
            except OSError as e:
                print('[ERROR] Could not open file: %s ... Exiting' % options.s)
                sys.exit(0)
        else:
            if verbose: print('[*] Reading secret from console input ...')
            secret = options.S[1:-1]
        if verbose: print('[*] DONE')

        try:
            encoded_list = encode(plain, secret, verbose)
        except ValueError as e:
            print(e)
            sys.exit(0)

        if not options.o == None:
            try:
                if verbose: print('[*] Writing to file %s' % options.o)
                f1 = open(options.o, 'w')
            except:
                print('[ERROR] Could not open file: %s ... Writing to stdout' % options.o)
                f1 = sys.stdout
        else:
            f1 = sys.stdout
        
        for word in encoded_list:
            f1.write(word)
            f1.write('\n')
        f1.close()

    elif sys.argv[1] == 'decode':
        if verbose: print('[*] Decode mode chosen')
        try:
            if verbose: print('[*] Reading encoded list from file ...')
            f1 = open(options.p, 'r')
            encoded_raw = f1.read()
            encoded_list = encoded_raw.split('\n')[:-1]
            f1.close()
        except OSError as e:
            print('[ERROR] Could not open file: %s ... Exiting' % options.p)
            sys.exit(0)
        if verbose: print('[*] DONE')
        
        secret, decoded_string = decode(encoded_list, verbose)
        
        if not options.o == None:
            try:
                if verbose: print('[*] Writing to file %s' % options.o)
                f1 = open(options.o, 'w')
            except:
                print('[ERROR] Could not open file: %s ... Writing to stdout' % options.o)
                f1 = sys.stdout
        else:
            f1 = sys.stdout

        carrier_flag = options.n
        if carrier_flag:
            f1.write('[*] Visible decoding\n')
            f1.write(decoded_string)
            f1.write('\n\n')
        f1.write('[*] Hidden message\n')
        f1.write(secret)
        f1.write('\n\n')
        f1.close()
