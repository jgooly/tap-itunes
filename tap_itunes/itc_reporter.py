"""This module is used send and return the response information from iTunes"""

import gzip
import json
import sys
import xml.etree.ElementTree as ET

import requests
import singer

SESSION = requests.session()
LOGGER = singer.get_logger()


def create_params(access_token, query, version, mode, account):
    """Builds a query string to send with the request."""

    json_request = json.dumps({"accesstoken": access_token,
                               "queryInput": query,
                               "version": version,
                               "mode": mode,
                               "account": account})

    return json_request


def get_subscription_report(access_token, version, mode, target_date, endpoint,
                            vendor, account, report_version):
    """Get the data from iTunes response.
    Returns data and filename Tuple.
    """

    query = "[p=Reporter.properties, Sales.getReport, {},Subscription,Summary,{},{},{}]".format(
        vendor, 'Daily', target_date, report_version)

    params = create_params(access_token, query, version, mode, account)

    response = send_request(endpoint, params)

    return output_data(response)


def get_subscription_event_report(access_token, version, mode, target_date,
                                  endpoint, vendor, account, report_version):
    """
    Get the subscriptions events report.
    :param access_token: access token; string
    :param version: version iTunes Reporter being used; string
    :param mode: the fetch mode (normal or robot); string
    :param target_date: data to fetch in format yyyymmdd; string
    :param endpoint: endpoint url; string
    :param vendor: iTunes Reporter vendor id; string
    :param account: iTunes Reporter account id; string
    :param report_version: iTunes Reporter report version; string
    :return: data and filename tuple
    """
    query = "[p=Reporter.properties, Sales.getReport, {}," \
            "SubscriptionEvent,Summary,{},{},{}]".format(
                vendor, 'Daily', target_date, report_version)

    params = create_params(access_token, query, version, mode, account)

    response = send_request(endpoint, params)

    return output_data(response)


def send_request(e_url, params):
    """Send request to iTunes and return the response."""

    header = {'Accept': 'text/html,image/gif,image/jpeg; q=.2, */*; q=.2'}

    req = requests.Request('POST', url=e_url,
                           params='jsonRequest={}'.format(params),
                           headers=header).prepare()

    try:
        response = SESSION.send(req)

        if not response.status_code == 200:
            message, content = get_content_item(response.content)

            if content == 210:
                LOGGER.warning(
                    'iTunes code: {}, message: {}'.format(content, message))
                sys.exit(1)
            else:
                LOGGER.error(
                    'iTunes code: {}, message: {}'.format(content, message))
                sys.exit(1)

    except requests.exceptions.RequestException as error:
        LOGGER.error(error)
        raise error

    return response


def output_data(response):
    """Unzip file and return data and file name."""

    data = gzip.decompress(response.content)
    data = data.decode('utf-8')
    file_name = response.headers['filename'].replace('.gz', '')

    return data, file_name


def get_content_item(content):
    """Parse response for Message and Code nodes."""

    tree = ET.fromstring(content)
    message = [child.text for child in tree.iter('Message')]
    code = [child.text for child in tree.iter('Code')]

    return message[0], int(code[0])
