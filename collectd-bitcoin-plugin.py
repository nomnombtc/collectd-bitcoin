from bitcoinrpc.authproxy import AuthServiceProxy
import collectd


RPC_USER = "change_me_to_your_rpc_username"
RPC_PASSWORD = "change_me_or_you_will_loose_money"
PROXY = ""


def init_func():
    authserv = "http://" + RPC_USER + ":" + RPC_PASSWORD + "@127.0.0.1:8332"
    global PROXY
    PROXY = AuthServiceProxy(authserv)


def read_nettotals():
    response = PROXY.getnettotals()
    funcname = str("getnettotals")
    for subkey in ['totalbytesrecv', 'totalbytessent']:
        total_bytes = response[subkey]
        val = collectd.Values(type='counter',
                              host='',
                              plugin='bitcoind',
                              time=0)
        val.plugin_instance = funcname
        val.type_instance = subkey
        val.dispatch(values=[total_bytes])


def read_networkinfo():
    response = PROXY.getnetworkinfo()
    funcname = str("getnetworkinfo")
    subkey = str("connections")
    number_of_connections = response[subkey]
    val = collectd.Values(type='gauge',
                          host='',
                          plugin='bitcoind',
                          time=0)
    val.plugin_instance = funcname
    val.type_instance = subkey
    val.dispatch(values=[number_of_connections])


def read_mempoolinfo():
    response = PROXY.getmempoolinfo()
    funcname = str("getmempoolinfo")
    for subkey in ['size', 'bytes']:
        info = response[subkey]
        val = collectd.Values(type='gauge',
                              host='',
                              plugin='bitcoind',
                              time=0)
        val.plugin_instance = funcname
        val.type_instance = subkey
        val.dispatch(values=[info])


def read_estimatesmartfee():
    # Starting with v0.17 only estimatesmartfee call is supported
    # Estimate cost to include the transaction within 6 blocks
    response = PROXY.estimatesmartfee(6)
    funcname = str("estimatesmartfee")
    feerate = response['feerate']
    val = collectd.Values(type='gauge',
                          host='',
                          plugin='bitcoind',
                          time=0)
    val.plugin_instance = funcname
    val.type_instance = funcname
    val.dispatch(values=[feerate])


def read_blockcount():
    # get size, height, diff of the last block
    response = PROXY.getblockcount()
    blockcount = response
    # get hash of last block
    response = PROXY.getblockhash(blockcount)
    blockhash = response
    # get info from blockhash
    response = PROXY.getblock(blockhash)
    funcname = str("getblock")
    for subkey in ['size', 'height', 'difficulty']:
        funccat = (str(funcname) + "_" + str(subkey))
        value = response[subkey]
        val = collectd.Values(type='gauge',
                              host='',
                              plugin='bitcoind',
                              time=0)
        val.plugin_instance = funccat
        val.type_instance = subkey
        val.dispatch(values=[value])


def read_networkhashps():
    # network hashrate
    response = PROXY.getnetworkhashps()
    funcname = str("getnetworkhashps")
    networkhashps = response
    val = collectd.Values(type='gauge',
                          host='',
                          plugin='bitcoind',
                          time=0)
    val.plugin_instance = funcname
    val.type_instance = funcname
    val.dispatch(values=[networkhashps])

def read_func():
    try:
        read_nettotals()
    except:
        collectd.error('bitcoin plugin: exception reading nettotals value!')

    try:
        read_networkinfo()
    except:
        collectd.error('bitcoin plugin: exception reading networkinfo!')

    try:
        read_mempoolinfo()
    except:
        collectd.error('bitcoin plugin: exception reading mempoolinfo!')

    try:
        read_estimatesmartfee()
    except:
        collectd.error('bitcoin plugin: exception reading estimatesmartfee!')

    try:
        read_blockcount()
    except:
        collectd.error('bitcoin plugin: exception reading blockcount!')

    try:
        read_networkhashps()
    except:
        collectd.error('bitcoin plugin: exception reading networkhasps!')


collectd.register_init(init_func)
collectd.register_read(read_func)