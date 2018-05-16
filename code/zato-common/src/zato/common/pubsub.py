# -*- coding: utf-8 -*-

"""
Copyright (C) 2017, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Zato
from zato.common.util import new_cid

# ################################################################################################################################

_skip_to_external=('delivery_status', 'topic_id', 'cluster_id', 'pattern_matched', 'published_by_id', 'data_prefix',
    'data_prefix_short', 'pub_time', 'expiration_time', 'ext_pub_time', 'pub_correl_id', 'pub_msg_id')

# ################################################################################################################################

def new_msg_id(_new_cid=new_cid):
    return 'zpsm%s' % _new_cid()

# ################################################################################################################################

def new_sub_key(_new_cid=new_cid):
    return 'zpsk%s' % _new_cid()

# ################################################################################################################################

def new_group_id(_new_cid=new_cid):
    return 'zpsg%s' % _new_cid()

# ################################################################################################################################

class PubSubMessage(object):
    """ Base container class for pub/sub message wrappers.
    """
    # We are not using __slots__ because they can't be inherited by subclasses
    # and this class, as well as its subclasses, will be rewritten in Cython anyway.
    _attrs = ('topic', 'sub_key', 'pub_msg_id', 'pub_correl_id', 'in_reply_to', 'ext_client_id', 'group_id', 'position_in_group',
        'pub_time', 'ext_pub_time', 'data', 'data_prefix', 'data_prefix_short', 'mime_type', 'priority', 'expiration',
        'expiration_time', 'has_gd', 'delivery_status', 'pattern_matched', 'size', 'published_by_id', 'topic_id',
        'is_in_sub_queue', 'topic_name', 'cluster_id', 'pub_time_iso', 'ext_pub_time_iso', 'expiration_time_iso')

    def __init__(self):
        self.topic = None
        self.sub_key = None
        self.pub_msg_id = None
        self.pub_correl_id = None
        self.in_reply_to = None
        self.ext_client_id = None
        self.group_id = None
        self.position_in_group = None
        self.pub_time = None
        self.ext_pub_time = None
        self.data = None
        self.data_prefix = None
        self.data_prefix_short = None
        self.mime_type = None
        self.priority = None
        self.expiration = None
        self.expiration_time = None
        self.has_gd = None
        self.delivery_status = None
        self.pattern_matched = None
        self.size = None
        self.published_by_id = None
        self.topic_id = None
        self.is_in_sub_queue = None
        self.topic_name = None
        self.cluster_id = None

        self.pub_time_iso = None
        self.ext_pub_time_iso = None
        self.expiration_time_iso = None

    def to_dict(self, skip=None, needs_utf8_encode=True, _data_keys=('data', 'data_prefix', 'data_prefix_short')):
        """ Returns a dict representation of self.
        """
        skip = skip or []
        out = {}
        for key in PubSubMessage._attrs:
            if key != 'topic' and key not in skip:
                value = getattr(self, key)
                if value is not None:
                    if needs_utf8_encode:
                        if key in _data_keys:
                            value = value.encode('utf8')
                    out[key] = value

        return out

    def to_external_dict(self, skip=_skip_to_external, needs_utf8_encode=False):
        """ Returns a dict representation of self ready to be delivered to external systems,
        i.e. without internal attributes on output.
        """
        out = self.to_dict(skip, needs_utf8_encode)
        out['msg_id'] = self.pub_msg_id
        out['correl_id'] = self.pub_correl_id

        return out

# ################################################################################################################################

class SkipDelivery(Exception):
    """ Raised to indicate to delivery tasks that a given message should be skipped - but not deleted altogether,
    the delivery will be attempted in the next iteration of the task.
    """

# ################################################################################################################################

class HandleNewMessageCtx(object):
    """ Encapsulates information on new messages that a pubsub tool is about to process.
    """
    __slots__ = ('cid', 'has_gd', 'sub_key_list', 'non_gd_msg_list', 'is_bg_call', 'pub_time_max')

    def __init__(self, cid, has_gd, sub_key_list, non_gd_msg_list, is_bg_call, pub_time_max=None):
        self.cid = cid
        self.has_gd = has_gd
        self.sub_key_list = sub_key_list
        self.non_gd_msg_list = non_gd_msg_list
        self.is_bg_call = is_bg_call
        self.pub_time_max = pub_time_max
