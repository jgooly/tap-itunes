# !/usr/bin/env python3

import tap_itunes.sync_subscription_event_stream
import tap_itunes.sync_subscription_stream
import singer
import pendulum

LOGGER = singer.get_logger()


def main():
    LOGGER.info('Running script now: {}'.format(pendulum.now()))
    sync_subscription_stream.sync_subscriptions()
    sync_subscription_event_stream.sync_subscription_events()
    LOGGER.info('All streams updated.')


if __name__ == "__main__":
    main()
