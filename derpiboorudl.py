#!/usr/bin/env python

from derpibooru import Search
from requests import get, codes
from hashlib import sha512

import argparse
import logging
import os
import os.path
import sys

logger = None

def sha512_hash(f):
    h = sha512()

    h.update(f)
    return h.hexdigest()

def download_file(url):
    r = get(url)

    if r.status_code == codes.ok:
        return r.content

def setup_logger(log):
    log.setLevel(logging.DEBUG)

    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    log.addHandler(ch)

def main():
    logger = logging.getLogger("derpiboorudl")
    setup_logger(logger)

    # Parse args
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--destdir", required=True, help="Location where downloaded images will be dropped off")
    parser.add_argument("-q", "--query", default="", help="The Derpibooru query you wish to execute")
    parser.add_argument("-c", "--count", default=100, help="The count of images you wish to download", type=int)
    parser.add_argument("-k", "--key", default=None, help="Specify the API key (normally present as env variable)")
    args = parser.parse_args()

    destdir, query, maximages = args.destdir, args.query, args.count
 
    # Read API key from --key if present or else read from env
    apikey = args.key if args.key else os.getenv("DERPIBOORUAPIKEY")

    if not apikey:
        logger.info("No API key was set! (DERPIBOORUAPIKEY)")

    search = Search().key(apikey).query(query).limit(maximages)

    if not os.path.isdir(destdir):
        os.mkdir(destdir)

    for image in search:
        filename = os.path.basename(image.full)
        path = os.path.join(destdir, filename)
        if not os.path.isfile(path):
            logger.info("Now downloading image with id {0}".format(image.id_number))

            download = download_file(image.full)
            if download:
                if image.sha512_hash == sha512_hash(download):
                    with open(path, "wb") as f:
                        f.write(download)
                else:
                    logger.error("sha512 hashes for {0} don't match up".format(image.id_number))
            else:
                logger.error("download for {0} didn't complete".format(image.id_number))


if __name__ == "__main__":
    main()

