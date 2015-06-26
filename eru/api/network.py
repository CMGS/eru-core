# coding: utf-8

from flask import Blueprint, request, current_app
from ipaddress import IPv4Interface, AddressValueError

from eru import consts
from eru.models import Network
from eru.utils.decorator import check_request_json, jsonify
from eru.utils.exception import EruAbortException

bp = Blueprint('network', __name__, url_prefix='/api/network')

@bp.route('/create/', methods=['POST'])
@jsonify
@check_request_json(['name', 'netspace'], consts.HTTP_BAD_REQUEST)
def create_network():
    data = request.get_json()
    n = Network.create(data['name'], data['netspace'])
    if not n:
        current_app.logger.info('Network create failed (name=%s, net=%s)',
                data['name'], data['netspace'])
        raise EruAbortException(consts.HTTP_BAD_REQUEST, 'Network create failed')
    current_app.logger.info('Network create succeeded (name=%s, net=%s)',
            data['name'], data['netspace'])
    return {'r': 0, 'msg': consts.OK}

@bp.route('/<int:network_id>/', methods=['GET'])
@jsonify
def get_network(network_id):
    n = Network.get(network_id)
    if not n:
        raise EruAbortException(consts.HTTP_NOT_FOUND, 'Network %s not found' % network_id)
    return n

@bp.route('/<string:network_name>/', methods=['GET'])
@jsonify
def get_network_by_name(network_name):
    n = Network.get_by_name(network_name)
    if not n:
        raise EruAbortException(consts.HTTP_NOT_FOUND, 'Network %s not found' % network_name)
    return n

@bp.route('/list/', methods=['GET'])
@jsonify
def list_networks():
    return Network.list_networks()

@bp.route('/addr/<path:addr>/available/', methods=['GET'])
@jsonify
def check_addr(addr):
    """addr is like 10.20.0.1/16 or 10.100.3.12/24"""
    try:
        interface = IPv4Interface(addr)
    except AddressValueError:
        raise EruAbortException(consts.HTTP_BAD_REQUEST, 'Not valid interface')
    net = Network.get_by_netspace(interface.network.compressed)
    if not net:
        raise EruAbortException(consts.HTTP_NOT_FOUND, 'Interface not found')
    return {'r': 0, 'msg': consts.OK, 'result': interface.ip in net}
