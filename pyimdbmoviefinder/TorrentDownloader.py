# This Python file uses the following encoding: utf-8
import httplib2
import logging
from json import dumps

logger = logging.getLogger('pyimdbmoviefinder')

class TorrentDownloader:
    '''
    Class allowing torrent download to a transmission daemon
    '''
    def __init__(self, host, user, pw, dir=None):
        self.host = host
        self.user = user
        self.pw = pw
        self.dir = dir

    def add_torrent_magnet(self, magnet_link:str) -> tuple[bool, str]:
        '''
        Forward the magnet link to transmission daemon through RPC
        magnet_link : the magnet link of the torrent to be sent
        return: Boolean result and String describing success / failure
        '''
        h = httplib2.Http(".cache")
        h.add_credentials(self.user, self.pw)
        try:
            resp, content = h.request(self.host, "GET")
        except Exception as e:
            return False, "Unable to send the request, verify your config : {}".format(str(e))
        if not 'x-transmission-session-id' in resp.keys():
            return False, "Response missing x-transmission-session-id, check your hostname/user/password or webserver configuration !"
        headers = { "X-Transmission-Session-Id": resp['x-transmission-session-id'] }
        args = { "filename": magnet_link }
        if self.dir:
            args['download-dir'] = self.dir
        body = dumps( { "method": "torrent-add",
                        "arguments": args } )
        _, content = h.request(self.host, 'POST', headers=headers, body=body)

        if str(content).find("success") == -1:
            logger.error("ERROR: Magnet Link: " + magnet_link)
            logger.error("ERROR: Answer: " + str(content))
            return False, "An error occured while sending torrent to {}. Server answered \r\n\"{}\"\
                \r\nMake sure the link is correct".format(self.host, str(content))
        return True, "Successfully added {} to {}".format(magnet_link, self.host)
