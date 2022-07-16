
class Config(object):
    WEB_PASSWORD = 'password'
    API_TOKEN = 'token'

    YOUR_TEAM = '10.1.21.1'
    TEAM_TOKEN = '' # team token for flag submission
    TEAMS = ['10.1.1.1'
,'10.1.3.1'
,'10.1.4.1'
,'10.1.6.1'
,'10.1.7.1'
,'10.1.8.1'
,'10.1.10.1'
,'10.1.11.1'
,'10.1.12.1'
,'10.1.14.1'
,'10.1.15.1'
,'10.1.16.1'
,'10.1.17.1'
,'10.1.18.1'
,'10.1.20.1'
,'10.1.21.1'
,'10.1.23.1'
,'10.1.24.1'
,'10.1.25.1'
,'10.1.28.1'
,'10.1.29.1'
,'10.1.30.1'
,'10.1.32.1'
,'10.1.34.1'
,'10.1.39.1'
,'10.1.41.1'
,'10.1.43.1'
,'10.1.44.1'
,'10.1.45.1'
,'10.1.48.1'
,'10.1.49.1'
,'10.1.50.1'
,'10.1.51.1'
,'10.1.52.1'
,'10.1.54.1'
,'10.1.55.1'
,'10.1.56.1'
,'10.1.57.1'
,'10.1.58.1'
,'10.1.59.1'
,'10.1.60.1']
    TEAMS.remove(YOUR_TEAM)

    ROUND_DURATION = 60
    FLAG_ALIVE = 10 * ROUND_DURATION
    FLAG_FORMAT = r'ENO[A-Za-z0-9+\/=]{48}'

    SUB_LIMIT = 1
    SUB_INTERVAL = 5
    SUB_TIMEOUT = SUB_INTERVAL / SUB_LIMIT
    SUB_PAYLOAD_SIZE = 100
    SUB_URL = 'tcp://10.0.13.37:1337' # 'http://10.1.0.2/flags' 'tcp://submission.faustctf.net:666/'

    SUB_TYPE = 'enowar' # enowar | faust | ccit | custom-http | custom-nc 
    
    ## for customs sub type
    CUSTOM_KEYWORDS = {
    'SUB_ACCEPTED'     : 'accepted',
    'SUB_INVALID'      : 'invalid',
    'SUB_OLD'          : 'too old',
    'SUB_YOUR_OWN'     : 'your own',
    'SUB_STOLEN'       : 'already stolen',
    'SUB_NOP'          : 'from NOP team',
    'SUB_NOT_AVAILABLE': 'is not available'
    }
    CUSTOM_SUBMITTER_FUNCTION = None

    # Don't worry about this
    DB_NSUB = 'NOT_SUBMITTED'
    DB_SUB = 'SUBMITTED'
    DB_SUCC = 'SUCCESS'
    DB_ERR = 'ERROR'
    DB_EXP = 'EXPIRED'

    SECRET_KEY = 'changeme'

    DATABASE = 'instance/flagWarehouse.sqlite'
    #################
