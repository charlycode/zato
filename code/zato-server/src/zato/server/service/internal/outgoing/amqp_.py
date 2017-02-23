# -*- coding: utf-8 -*-

"""
Copyright (C) 2011 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from contextlib import closing
from traceback import format_exc

# Zato
from zato.common.broker_message import OUTGOING
from zato.common.odb.model import ConnDefAMQP, OutgoingAMQP
from zato.common.odb.query import out_amqp_list
from zato.server.service import AsIs, Integer
from zato.server.service.internal import AdminService, AdminSIO, GetListAdminSIO

class GetList(AdminService):
    """ Returns a list of outgoing AMQP connections.
    """
    name = 'zato.outgoing.amqp.get-list'
    _filter_by = OutgoingAMQP.name,

    class SimpleIO(GetListAdminSIO):
        request_elem = 'zato_outgoing_amqp_get_list_request'
        response_elem = 'zato_outgoing_amqp_get_list_response'
        input_required = ('cluster_id',)
        output_required = ('id', 'name', 'is_active', 'def_id', 'delivery_mode', 'priority', 'def_name')
        output_optional = ('content_type', 'content_encoding', 'expiration', AsIs('user_id'), AsIs('app_id'))

    def get_data(self, session):
        return self._search(out_amqp_list, session, self.request.input.cluster_id, False)

    def handle(self):
        with closing(self.odb.session()) as session:
            self.response.payload[:] = self.get_data(session)

class Create(AdminService):
    """ Creates a new outgoing AMQP connection.
    """
    name = 'zato.outgoing.amqp.create'

    class SimpleIO(AdminSIO):
        request_elem = 'zato_outgoing_amqp_create_request'
        response_elem = 'zato_outgoing_amqp_create_response'
        input_required = ('cluster_id', 'name', 'is_active', 'def_id', 'delivery_mode', 'priority')
        input_optional = ('content_type', 'content_encoding', 'expiration', AsIs('user_id'), AsIs('app_id'))
        output_required = ('id', 'name')

    def handle(self):
        input = self.request.input

        input.delivery_mode = int(input.delivery_mode)
        input.priority = int(input.priority)

        if not(input.priority >= 0 and input.priority <= 9):
            msg = 'Priority should be between 0 and 9, not [{0}]'.format(repr(input.priority))
            raise ValueError(msg)

        with closing(self.odb.session()) as session:
            # Let's see if we already have a definition of that name before committing
            # any stuff into the database.
            existing_one = session.query(OutgoingAMQP.id).\
                filter(ConnDefAMQP.cluster_id==input.cluster_id).\
                filter(OutgoingAMQP.def_id==ConnDefAMQP.id).\
                filter(OutgoingAMQP.name==input.name).\
                first()

            if existing_one:
                raise Exception('An outgoing AMQP connection `{}` already exists on this cluster'.format(input.name))

            try:
                item = OutgoingAMQP()
                item.name = input.name
                item.is_active = input.is_active
                item.def_id = input.def_id
                item.delivery_mode = input.delivery_mode
                item.priority = input.priority
                item.content_type = input.content_type
                item.content_encoding = input.content_encoding
                item.expiration = input.expiration
                item.user_id = input.user_id
                item.app_id = input.app_id

                session.add(item)
                session.commit()

                input.action = OUTGOING.AMQP_CREATE.value
                input.def_name = item.def_.name
                self.broker_client.publish(input)

                self.response.payload.id = item.id
                self.response.payload.name = item.name

            except Exception, e:
                self.logger.error('Could not create an outgoing AMQP connection, e:`%s`', format_exc(e))
                session.rollback()

                raise

class Edit(AdminService):
    """ Updates an outgoing AMQP connection.
    """
    name = 'zato.outgoing.amqp.edit'

    class SimpleIO(AdminSIO):
        request_elem = 'zato_outgoing_amqp_edit_request'
        response_elem = 'zato_outgoing_amqp_edit_response'
        input_required = ('id', 'cluster_id', 'name', 'is_active', 'def_id', 'delivery_mode', Integer('priority'))
        input_optional = ('content_type', 'content_encoding', 'expiration', AsIs('user_id'), AsIs('app_id'))
        output_required = ('id', 'name')

    def handle(self):

        input = self.request.input

        input.delivery_mode = int(input.delivery_mode)
        input.priority = int(input.priority)

        if not(input.priority >= 0 and input.priority <= 9):
            msg = 'Priority should be between 0 and 9, not [{0}]'.format(repr(input.priority))
            raise ValueError(msg)

        with closing(self.odb.session()) as session:
            # Let's see if we already have a definition of that name before committing
            # any stuff into the database.
            existing_one = session.query(OutgoingAMQP.id).\
                filter(ConnDefAMQP.cluster_id==input.cluster_id).\
                filter(OutgoingAMQP.def_id==ConnDefAMQP.id).\
                filter(OutgoingAMQP.name==input.name).\
                filter(OutgoingAMQP.id!=input.id).\
                first()

            if existing_one:
                raise Exception('An outgoing AMQP connection `{}` already exists on this cluster'.format(input.name))

            try:
                item = session.query(OutgoingAMQP).filter_by(id=input.id).one()
                item.name = input.name
                item.is_active = input.is_active
                item.def_id = input.def_id
                item.delivery_mode = input.delivery_mode
                item.priority = input.priority
                item.content_type = input.content_type
                item.content_encoding = input.content_encoding
                item.expiration = input.expiration
                item.user_id = input.user_id
                item.app_id = input.app_id

                session.add(item)
                session.commit()

                input.action = OUTGOING.AMQP_EDIT.value
                input.def_name = item.def_.name
                self.broker_client.publish(input)

                self.response.payload.id = item.id
                self.response.payload.name = item.name

            except Exception, e:
                self.logger.error('Could not update the outgoing AMQP connection, e:`%s`', format_exc(e))
                session.rollback()

                raise

class Delete(AdminService):
    """ Deletes an outgoing AMQP connection.
    """
    name = 'zato.outgoing.amqp.delete'

    class SimpleIO(AdminSIO):
        request_elem = 'zato_outgoing_amqp_delete_request'
        response_elem = 'zato_outgoing_amqp_delete_response'
        input_required = ('id',)

    def handle(self):
        with closing(self.odb.session()) as session:
            try:
                item = session.query(OutgoingAMQP).\
                    filter(OutgoingAMQP.id==self.request.input.id).\
                    one()

                item_id = item.id
                def_name = item.def_.name

                session.delete(item)
                session.commit()

                self.broker_client.publish({
                    'action': OUTGOING.AMQP_DELETE.value,
                    'name': item.name,
                    'id':item_id,
                    'def_name':def_name,
                })

            except Exception, e:
                session.rollback()
                self.logger.error('Could not delete the outgoing AMQP connection, e:`%s`', format_exc(e))

                raise