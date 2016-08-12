#!/usr/bin/env python

# This is based on a python script from C-Otto found at:
# https://gist.github.com/C-Otto/a9e4864dff1a2b167761
#
# Biggest change is that it uses rpc connection instead of calling
# bitcoin-cli binary and added some more stuff to log.

import os
import sys
import time
import socket
from bitcoinrpc.authproxy import AuthServiceProxy

hostname = os.environ['COLLECTD_HOSTNAME'] if 'COLLECTD_HOSTNAME' in os.environ else socket.getfqdn()
interval = float(os.environ['COLLECTD_INTERVAL']) if 'COLLECTD_INTERVAL' in os.environ else 30
authserv = "http://rpcuser:rpcpassword@127.0.0.1:8332"

def main():
    while True:
        try:
                access = AuthServiceProxy(authserv)
                function = access.getnettotals()
                funcname = str("getnettotals")
                for subkey in ['totalbytesrecv', 'totalbytessent']:
                    value = function[subkey]
                    printValue("counter", funcname, funcname, subkey, value)

                function = access.getnetworkinfo()
                funcname = str("getnetworkinfo")
                subkey = str("connections")
                value = function[subkey]
                printValue("gauge", subkey, funcname, subkey, value)

                function = access.getmempoolinfo()
                funcname = str("getmempoolinfo")
                for subkey in ['size', 'bytes']:
                    value = function[subkey]
                    #without this it will appear "stacked" in CGP Panel
                    funccat = (str(funcname) + "_" + str(subkey))
                    printValue("gauge", funccat, funcname, subkey, value)
                
                #since 0.12 estimatefee 1 fails. Use estimatefee 2 instead.
                #see https://github.com/bitcoin/bitcoin/issues/7545
                function = access.estimatefee(2)
                funcname = str("estimatefee")
                value = function
                printValue("gauge", funcname, funcname, funcname, value)

                #get size, height, diff of the last block
                function = access.getblockcount()
                blockcount = function
                #get hash of last block
                function = access.getblockhash(blockcount)
                blockhash = function
                #get info from blockhash
                function = access.getblock(blockhash)
                funcname = str("getblock")
                for subkey in ['size', 'height', 'difficulty']:
                    funccat = (str(funcname) + "_" + str(subkey))
                    value = function[subkey]
                    printValue("gauge", funccat, funcname, subkey, value)

                #network hashrate
                function = access.getnetworkhashps()
                funcname = str("getnetworkhashps")
                value = function
                printValue("gauge", funcname, funcname, funcname, value)
        except:
                pass

        sys.stdout.flush()
        time.sleep(interval)

def printValue(dstype, funccat, function, subkey, value):
        print('PUTVAL "%s/bitcoin-%s/%s-%s_%s" interval=%s N:%s' % (hostname, funccat, dstype, function, subkey, interval, value))

if __name__ == '__main__':
    main()
