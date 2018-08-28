import argparse
import pendulum
import singer

import tap_itunes.itc_reporter as itc_reporter
import tap_itunes.utils as utils

PARSER = argparse.ArgumentParser()
PARSER.add_argument(
    '-c', '--config', help='Config file', required=True)
PARSER.add_argument(
    '-s', '--state', help='State file')

ARGS = PARSER.parse_args()
LOGGER = singer.get_logger()
CONFIG = utils.load_tap_setting(path=ARGS.config)
STATE_DATE_FORMAT = '%Y-%m-%d'
ITUNES_REQUEST_DATE_FORMAT = '%Y%m%d'
TIMEZONE = 'America/Los_Angeles'

SUBSCRIPTION_EVENT_SCHEMA = utils.load_schema('subscription_event')

# Determine if the streams need to be updated.
def find_state():
    try:
        stream_states = utils.load_tap_setting(ARGS.state)
        state = stream_states['subscription_event']

        LOGGER.info(
            'Found starting state for subscription event stream: {}'.format(
                state.format(STATE_DATE_FORMAT)))
    except TypeError:
        state = CONFIG['start_date']

        LOGGER.info(
            'No starting state found. Using config start date: {}'.format(
                state.format(STATE_DATE_FORMAT)))

    return state


def sync_date(dates_to_fetch,
              subscription_event_schema_,
              timezone=TIMEZONE,
              state_date_format=STATE_DATE_FORMAT,
              config=CONFIG):
    if len(dates_to_fetch) == 0:
        LOGGER.info('Subscription event stream is up to date.')
    else:
        singer.write_schema('itunes_subscriptions_event',
                            subscription_event_schema_,
                            list())
        for next_date in dates_to_fetch:
            next_date = pendulum.parse(next_date, tz=timezone)

            LOGGER.info('Starting sync for {}'.format(
                next_date.format(state_date_format)))

            # store list of itc arguments
            itc_args = {'access_token': config['accessToken'],
                        'version': config['version'],
                        'mode': config['mode'],
                        'target_date': next_date.format(
                            ITUNES_REQUEST_DATE_FORMAT),
                        'vendor': config['vendor'],
                        'endpoint': config['endpoint_sales'],
                        'account': config['account'],
                        'report_version': config['report_version']}

            # Get data for the given date.
            data, _ = itc_reporter.get_subscription_event_report(**itc_args)

            # Transform specific data to make sure they are encoded correctly from
            # string to int or float.
            to_transform = utils.get_special_schema_types(
                subscription_event_schema_['properties'])

            the_headers, the_data = utils.data_extraction(data)

            utils.process_records(the_headers, the_data, next_date,
                                  to_transform['int_keys'],
                                  to_transform['float_keys'],
                                  schema='itunes_subscriptions_event')
            if ARGS.state:
                prior_state = utils.load_tap_setting(ARGS.state)

                prior_state['subscription_event'] = next_date.format(
                    state_date_format)

                utils.write_state(prior_state, ARGS.state)


def sync_subscription_events():
    current_state = find_state()
    dates_to_fetch = utils.gen_dates(current_state, STATE_DATE_FORMAT)
    sync_date(dates_to_fetch, SUBSCRIPTION_EVENT_SCHEMA)

    LOGGER.info('Finished sync for itunes_subscription_event stream.')

sync_subscription_events()