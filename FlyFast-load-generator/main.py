#!/usr/bin/env python3

# /**********************************/
# /*       Copyright (c) 2022       */
# /*          Aternity LLC          */
# /*      All Rights Reserved.      */
# /**********************************/

# standard imports

import logging
import sys

import json
import random
import time
import http.client
import urllib.parse
import argparse

# site-package imports

TYPEAHEAD_URI_FMT = "/flightsearchapi/airportypeahead?searchtxt={text}&limit={limit}&qid={qid}"
ONE_WAY_URI_FMT = "/flightsearchapi/searchflight?from={from}&to={to}&departure={departureDate}&seat={seatType}&qid={qid}"
TWO_WAY_URI_FMT = "/flightsearchapi/searchflight?from={from}&to={to}&departure={departureDate}&return={returnDate}&seat={seatType}&qid={qid}"

SEAT_TYPE_TABLE = [ "Economy", "Premium Economy", "Business", "First" ]

SECONDS_PER_DAY = (60 * 60) * 24

logger = logging.getLogger("ff_load")

# * the airport list is generated at startup
g_airport_list = []

def pick_airports():

    # * use the global list here
    # * we are altering the list, which should be fine

    airports = g_airport_list
    cnt = len(airports)
    idx = random.randint(0, cnt - 1) # this includes both ends

    # * now swap them
    #   or we could just pick 2nd one below or above the first

    #   if idx < cnt / 2:
    #       # pick from upper set
    #       lo = idx + 1
    #       hi = cnt - 1
    #   else:
    #       # pick from lower set
    #       lo = 0
    #       hi = idx - 1

    # * here for swapping; swapping = swap the selected item with the last item

    x = airports[idx]

    lo = 0
    hi = cnt - 2
    if idx == cnt - 1:
        # nothing to do; the last item was selected
        pass
    else:
        # swap them here
        last = airports[cnt - 1]
        airports[cnt - 1] = x
        airports[idx] = last

    idx = random.randint(lo, hi)
    y = airports[idx]

    if x == y:
        logger.warning("internal error; airports are same [%s]=[%s]", x, y)

    tup = (x, y)
    return tup



def utc_to_str(utc):

    # this is format the api is expecting
    date_format = "%m-%d-%Y"

    tup = time.localtime(utc)
    return time.strftime(date_format, tup)


def pick_dates():

    # pick random date slightly in the future
    t0 = int(time.time())
    days = random.randint(2, 10)
    t0 += days * SECONDS_PER_DAY

    # pick random date after the first date
    days = random.randint(2, 10)
    t1 = t0 + days * SECONDS_PER_DAY

    t0_str = utc_to_str(t0)
    t1_str = utc_to_str(t1)

    tup = (t0_str, t1_str)
    return tup

def pick_seat_type():

    table = SEAT_TYPE_TABLE
    cnt = len(table)
    idx = random.randint(0, cnt - 1)
    return table[idx]

def build_flight_ht(qid=0):

    seat_type = pick_seat_type()
    dates = pick_dates()        # returns a tup
    airports = pick_airports()  # returns a tup

    # note: one 'seat_type' has a space so be sure to handle that properly
    seat_type = urllib.parse.quote(seat_type)
    ht = {}
    ht["seatType"] = seat_type
    ht["departureDate"] = dates[0]
    ht["returnDate"] = dates[1]
    ht["from"] = airports[0]
    ht["to"] = airports[1]
    ht["qid"] = qid

    return ht


def build_one_way_uri(qid=0):

    ht = build_flight_ht(qid)
    uri = ONE_WAY_URI_FMT.format(**ht)

    return uri

def build_two_way_uri(qid=0):

    ht = build_flight_ht(qid)
    uri = TWO_WAY_URI_FMT.format(**ht)

    return uri

def build_typeahead_uri(qid=0):

    ht = {}
    idx = random.randint(0, 25)
    ht["text"] = chr(ord("a") + idx)
    ht["limit"] = random.randint(5, 50) # this is currently ignored
    ht["qid"] = qid

    uri = TYPEAHEAD_URI_FMT.format(**ht)

    return uri


FWD_SLASH = "/"

# * NOTE, the very first query is getting the airports, so let's
#         have that one-time query use qid=0;
# * this way we can (sorta) confirm when the app started

# pylint: disable=broad-except

def do_basic_rest_api(opts, uri):

    # host = opts.host
    # port = opts.port
    # ignore_response = opts.ignore_response
    # verbose = opts.verbose

    method = "GET"

    if not uri.startswith(FWD_SLASH):
        uri = FWD_SLASH + uri

    obj = {}
    body = ""

    # do we want special handling for a timeout?
    try:
        conn = http.client.HTTPConnection(host=opts.host, port=opts.port, timeout=opts.timeout)
        conn.request(method, uri, body)

        if opts.ignore_response:
            # don't pause and try to read the response
            if opts.verbose:
                logger.info("ignore response : %s", uri)
        else:
            response = conn.getresponse()

            txt = response.read()
            if opts.verbose:
                logger.info("response len=[%8s] : %s", len(txt), uri)
            obj = json.loads(txt)

    except Exception as e:
        # log this...
        logger.error("uri=[%s]; e=[%s]", uri, str(e))

    return obj

# pylint: enable=broad-except


def do_one_set(opts, cnt, qid):

    table = [
        build_typeahead_uri,
        # build_one_way_uri,    # skip this one
        build_two_way_uri,
    ]

    for _ in range(0, cnt):
        for f in table:
            uri = f(qid=qid)
            do_basic_rest_api(opts=opts, uri=uri)
            qid += 1
            if qid == 10000:
                # sure, lets wrap the id
                qid = 1

    return qid


def sleep_until(next_ts, next_cnt):

    now = time.time()
    dt = next_ts - now
    if dt < 0:
        logger.warning("next_cnt=[%6s]; code isn't keeping up; not sleeping; dt=[%.3f]",
                       next_cnt,
                       dt)
    else:
        logger.info("next_cnt=[%6s]; sleeping [%6.2f seconds]", next_cnt, dt)
        time.sleep(dt)


def run_forever(opts):

    #   host = opts.host
    #   port = opts.port
    #   num_minutes = opts.num_minutes
    #   ignore_response = opts.ignore_response
    #   verbose = opts.verbose

    cnt_table = opts.steps

    # * run in the next minute
    # * try and run 10 seconds into the minute; i.e. around hh:mm:10
    # * this should help avoid any ntp issues

    next_ts = int(time.time())
    next_ts -= (next_ts % 60)   # round down to the current minute
    next_ts += 70               # pick 10 seconds into the next minute

    nth = 0
    # cnt_table = [ 10, 20, 40, 80, 40, 20, 10 ]
    # cnt_table = [ 4, 6, 8, 16, 8, 6, 4]
    # cnt_table = [ 5, 10, 15, 20, 20, 15, 10, 5 ]
    # cnt_table = [ 80, 100, 100, 80 ]
    # cnt_table = [ 80, 120, 160, 120, 80 ]

    qid = 1
    num_minutes = opts.num_minutes
    max_cycle_time = 40
    while True:
        cnt = cnt_table[nth]
        nth += 1
        if nth == len(cnt_table):
            nth = 0

        for _ in range(0, num_minutes):
            sleep_until(next_ts, cnt)
            #
            #  to avoid ntp issues we really want to send data between:
            #       * seconds:  10 and 50
            #       * i.e. [minute:10, minute:50) 
            # 
            t0 = time.time()
            qid = do_one_set(opts, cnt, qid)
            dt = time.time() - t0
            if dt > max_cycle_time:
                logger.warning("cycle took more than %6s seconds; [%6.2f seconds]", 
                               max_cycle_time,
                               dt)
            else:
                # this is temp
                # logger.info("cycle took [%6.2f seconds]", dt)
                pass
            next_ts += 60

        # ok now update the count


def init_airports(opts):

    ht = {}
    ht["text"] = "a"    # 'a' seems to match all airports
    ht["limit"] = 500   # this is currently ignored; 615 items typically found
    ht["qid"] = 0

    uri = TYPEAHEAD_URI_FMT.format(**ht)

    # CORRECT: must process the response here

    ignore_response = opts.ignore_response
    opts.ignore_response = False
    items = []
    sleep_seconds = 30
    while True:
        items = do_basic_rest_api(opts=opts, uri=uri)
        if len(items) == 0:
            logger.info("unable to get airports; sleeping [%3s seconds]...", sleep_seconds)
            time.sleep(sleep_seconds)
        else:
            break

    # restore this value
    opts.ignore_response = ignore_response

    #       {
    #       "value": "ABE",
    #       "name": "Lehigh Valley International Airport",
    #       "city": "ALLENTOWN",
    #       "region": "PENNSYLVANIA",
    #       "country": "USA"
    #       },
    #
    # * we'll make sure we don't get any duplicate values here.
    dst = []
    ap_ht = {} # airport hashtable
    for ht in items:
        value = ht.get("value", None)
        if value:
            x = ap_ht.get(value, False)
            if x:
                logger.warning("duplicate airport value=[%s]", value)
            else:
                dst.append(value)
                ap_ht[value] = True

    logger.info("initalized airports; cnt=[%6s]", len(dst))

    return dst


# ------------------------------------------
# pylint: disable=too-many-locals
# pylint: disable=global-statement

def main():

    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s %(levelname)-7s : %(name)-15s : %(message)s",
                        datefmt="%Y-%m-%d %H:%M:%S",
                        stream=sys.stdout)     # or stream=sys.stderr

    # steps = [ 10, 20, 40, 80, 160, 80, 40, 20, 10 ]
    steps = [ 2, 4, 8, 16, 8, 4 ]
    argp = argparse.ArgumentParser()
    argp.add_argument("-host", dest="host", default="", action="store")
    argp.add_argument('-port', dest='port', type=int, default=80, action='store')
    argp.add_argument('-num_minutes', dest='num_minutes', type=int, default=2, action='store')
    argp.add_argument('-timeout', dest='timeout', type=int, default=10, action='store')
    argp.add_argument('-steps', dest='steps', type=int, nargs='+', default=steps)
    argp.add_argument("-ignore_response", dest="ignore_response", default=False, action="store_true")
    argp.add_argument("-verbose", dest="verbose", default=False, action="store_true")
    args = argp.parse_args()
    opts = args

    if opts.host == "":
        logger.info("please supply -host on the command line")
        return

    logger.info("starting...")

    logger.info("#---------------------")
    ht = vars(opts)
    keys = list(ht.keys())
    keys.sort()
    for k in keys:
        v = ht[k]
        logger.info("%-15s = %s", k, v)

    logger.info("#---------------------")

    # * setting the global here
    # * hmmm, pylint complains about the global though.
    global g_airport_list

    g_airport_list = init_airports(opts)
    run_forever(opts)

    return

# pylint: enable=too-many-locals
# pylint: enable=global-statement
# ------------------------------------------


if __name__ == "__main__":
    try:
        main()
        # main_profile ()
    except KeyboardInterrupt:
        print("x interrupted.")

