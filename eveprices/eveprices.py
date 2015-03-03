import httplib
import xmltodict
from couchbase import Couchbase
from couchbase.exceptions import CouchbaseError

class eveprices:
    def __init__(self, priceType='e43', echost='api.eve-central.com', e43host='element-43.com',
                 psqlhost = 'localhost', psqlname='element43', psqluser='element43', psqlpass = 'element43',
                 psqlport = '6432', cbserver = '127.0.0.1', regionID = 10000002, cbucket='prices', cbpass='prices'):
        self.priceType = priceType
        self.echost = echost
        self.e43host = e43host
        self.psqlhost = psqlhost
        self.psqlname = psqlname
        self.psqluser = psqluser
        self.psqlpass = psqlpass
        self.psqlport = psqlport
        self.cache = Couchbase.connect(cbucket, cbserver, password=cbpass)
        self.regionID = int(regionID)
        typeID = 0

    def getPrice(self, typeID, orderType='buy', dataType='median'):
        """
        Retreives prices from the various price providers for eve-online.

        @param int typeID       Eve-online TypeID, no error checking involved
        @param string orderType Pulling buy or sell order data
        @param string dataType  mean/median/max/min pricing data
        """
        typeID = int(typeID)
        key = str(typeID) + str(self.regionID) + self.priceType
        try:
            priceData = self.cache.get(key).value
        except CouchbaseError:
            if self.priceType == 'e43':
                priceData = self.e43pricing(typeID)
            elif self.priceType == 'psql':
                priceData = self.psqlpricing(typeID)
            else:
                priceData = self.ecpricing(typeID)
            self.cache.add(key, priceData, ttl=1200)
        return float(priceData[orderType][dataType])

    def ecpricing(self, typeID):
        """
        Retreives prices from Eve-Central
        """
        conn = httplib.HTTPConnection(self.echost)
        conn.request("GET", "/api/marketstat/?typeid=%i&regionlimit=%i" % (typeID, self.regionID))
        res = conn.getresponse()
        try:
            content = res.read()
            if content == "The request contains bad syntax or cannot be fulfilled.":
                raise ValueError
            marketRaw = xmltodict.parse(content)
            conn.close()
            retVal = {
                'buy': {
                    'mean': marketRaw['evec_api']['marketstat']['type']['buy']['avg'],
                    'max': marketRaw['evec_api']['marketstat']['type']['buy']['max'],
                    'min': marketRaw['evec_api']['marketstat']['type']['buy']['min'],
                    'median': marketRaw['evec_api']['marketstat']['type']['buy']['median'],
                    'volume': marketRaw['evec_api']['marketstat']['type']['buy']['volume'],
                },
                'sell': {
                    'mean': marketRaw['evec_api']['marketstat']['type']['sell']['avg'],
                    'max': marketRaw['evec_api']['marketstat']['type']['sell']['max'],
                    'min': marketRaw['evec_api']['marketstat']['type']['sell']['min'],
                    'median': marketRaw['evec_api']['marketstat']['type']['sell']['median'],
                    'volume': marketRaw['evec_api']['marketstat']['type']['buy']['volume'],
                },
            }
        except:
            conn.close()
            retVal = {
                'buy': {
                    'mean': 0,
                    'max': 0,
                    'min': 0,
                    'median': 0,
                },
                'sell': {
                    'mean': 0,
                    'max': 0,
                    'min': 0,
                    'median': 0,
                },
            }
        return retVal

    def e43pricing(self, typeID):
        conn = httplib.HTTPConnection(self.e43host)
        conn.request("GET", "/market/api/marketstat/?typeid=%i&regionlimit=%i" % (typeID, self.regionID))
        res = conn.getresponse()
        try:
            content = res.read()
            if content == "The request contains bad syntax or cannot be fulfilled.":
                raise ValueError
            marketRaw = xmltodict.parse(content)
            conn.close()
            retVal = {
                'buy': {
                    'mean': marketRaw['evec_api']['marketstat']['type']['buy']['avg'],
                    'max': marketRaw['evec_api']['marketstat']['type']['buy']['max'],
                    'min': marketRaw['evec_api']['marketstat']['type']['buy']['min'],
                    'median': marketRaw['evec_api']['marketstat']['type']['buy']['median'],
                },
                'sell': {
                    'mean': marketRaw['evec_api']['marketstat']['type']['sell']['avg'],
                    'max': marketRaw['evec_api']['marketstat']['type']['sell']['max'],
                    'min': marketRaw['evec_api']['marketstat']['type']['sell']['min'],
                    'median': marketRaw['evec_api']['marketstat']['type']['sell']['median'],
                },
            }
        except:
            conn.close()
            retVal = {
                'buy': {
                    'mean': 0,
                    'max': 0,
                    'min': 0,
                    'median': 0,
                },
                'sell': {
                    'mean': 0,
                    'max': 0,
                    'min': 0,
                    'median': 0,
                },
            }
        return retVal


    def psqlpricing(self, typeID):
        import psycopg2
        import psycopg2.extras
        # Handle DBs without password
        if not dbpass:
        # Connect without password
            dbcon = psycopg2.connect("host="+self.psqlhost+" user="+self.psqluser+" dbname="+self.psqlname+" port="+self.psqlport)
        else:
            dbcon = psycopg2.connect("host="+self.psqlhost+" user="+self.psqluser+" password="+self.psqlpass+" dbname="+self.psqlname+" port="+self.psqlport)
        curs = dbcon.cursor(cursor_factory=psycopg2.extras.DictCursor)
        curs.execute("""select * from market_data_itemregionstat where mapregion_id = %s and invtype_id = %s """, (self.regionID, typeID))
        data = curs.fetchone()
        curs.execute("""select price from market_data_orders where invtype_id = %s and mapregion_id = %s and is_active = 't' and is_bid = 't' order by price desc limit 1""", (typeID, self.regionID))
        buy_max = curs.fetchone()
        curs.execute("""select price from market_data_orders where invtype_id = %s and mapregion_id = %s and is_active = 't' and is_bid = 't' order by price asc limit 1""", (typeID, self.regionID))
        buy_min = curs.fetchone()
        curs.execute("""select price from market_data_orders where invtype_id = %s and mapregion_id = %s and is_active = 't' and is_bid = 'f' order by price desc limit 1""", (typeID, self.regionID))
        sell_max = curs.fetchone()
        curs.execute("""select price from market_data_orders where invtype_id = %s and mapregion_id = %s and is_active = 't' and is_bid = 'f' order by price asc limit 1""", (typeID, self.regionID))
        sell_min = curs.fetchone()
        retVal = {
            'buy': {
                'mean': data['buymean'],
                'max': buy_max[0],
                'min': buy_min[0],
                'median': data['buymedian'],
            },
            'sell': {
                'mean': data['sellmean'],
                'max': sell_max[0],
                'min': sell_min[0],
                'median': data['sellmedian'],
            },
        }
        return retVal
