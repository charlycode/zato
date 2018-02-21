# -*- coding: utf-8 -*-

"""
Copyright (C) 2018, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# SQLAlchemy
from sqlalchemy import or_

# Zato
from zato.common.odb.model import SSOUser

# ################################################################################################################################

_skip_user_columns=('password',)
_user_basic_columns = [elem for elem in SSOUser.__table__.c if elem not in _skip_user_columns]
_user_exists_columns = [SSOUser.user_id, SSOUser.username, SSOUser.email]

# ################################################################################################################################

def user_exists(session, username, email, check_email):
    """ Returns a boolean flag indicating whether user exists by username or email.
    """
    if check_email:
        condition = or_(SSOUser.username==username, SSOUser.email==email)
    else:
        condition = SSOUser.username==username

    return session.query(*_user_exists_columns).\
        filter(condition).\
        first()

# ################################################################################################################################

def _get_user(session):
    return session.query(*_user_basic_columns)

# ################################################################################################################################

def get_user_by_id(session, user_id):
    return _get_user(session).\
        filter(SSOUser.user_id==user_id).\
        first()

# ################################################################################################################################

def get_user_by_username(session, username):
    return _get_user(session).\
        filter(SSOUser.username==username).\
        first()

# ################################################################################################################################