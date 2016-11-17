# -*-coding:utf-8-*-
import random
import logging

logger = logging.getLogger(__name__)


class ProxyMiddleware(object):
    def process_request(self, request, spider):
        proxy_ip = random.choice(self.user_agent_ip_list)
        try:
            # print(unicode(proxy_ip).encode("utf-8"))
            request.meta['proxy'] = proxy_ip
        except Exception,msg:
            logger.info(msg)
        logger.info('%s' % proxy_ip)

    user_agent_ip_list = [
                          "http://60.12.75.90:80",
                          "http://210.14.64.59:80"
                          ]
