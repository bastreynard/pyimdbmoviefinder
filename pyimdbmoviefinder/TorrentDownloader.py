'''
This modules allows sending a magnet torrent link to a running transmission daemon
'''

import logging
from json import dumps
import httplib2

logger = logging.getLogger('pyimdbmoviefinder')

class TorrentDownloader:
    '''
    Class allowing torrent download to a transmission daemon
    '''

    def __init__(self, host, user, pw, directory=None):
        '''Constructor'''
        self.host = host
        self.user = user
        self.pw = pw
        self.dir = directory

    def add_torrent_magnet(self, magnetLink: str) -> tuple[bool, str]:
        """Forward the magnet link to transmission daemon through RPC

        Args:
            magnetLink (str): the magnet link of the torrent to be sent

        Returns:
            tuple[bool, str]: Boolean result and String describing success / failure
        """
        h = httplib2.Http(".cache")
        h.add_credentials(self.user, self.pw)
        try:
            resp, content = h.request(self.host, "GET")
        except Exception as e: #pylint: disable=broad-exception-caught
            return False, ("Unable to send the request, verify your config : %s", str(e))
        if not 'x-transmission-session-id' in resp.keys():
            return False, "Response missing x-transmission-session-id, check your \
                hostname/user/password or webserver configuration !"
        headers = {
            "X-Transmission-Session-Id": resp['x-transmission-session-id']}
        args = {"filename": magnetLink}
        if self.dir:
            args['download-dir'] = self.dir
        body = dumps({"method": "torrent-add",
                      "arguments": args})
        _, content = h.request(self.host, 'POST', headers=headers, body=body)

        if str(content).find("success") == -1:
            logger.error("ERROR: Magnet Link: %s", magnetLink)
            logger.error("ERROR: Answer: %s", str(content))
            return False, "An error occured while sending torrent to" + self.host + \
                "Server answered \r\n" + str(content) + " \r\nMake sure the link is correct"
        return True, "Successfully added " + magnetLink + self.host
