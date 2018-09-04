"""This module contains a small collection of helper functions."""

import json
import os
import re
import singer
import pendulum


def get_abs_path(path):
    """Returns the absolute path."""
    return os.path.join(os.path.dirname(os.path.realpath(__file__)), path)


def get_json(path):
    """Loads a .json file."""
    json_data = open(path)
    data = json.load(json_data)
    json_data.close()

    return data


def load_schema(entity):
    """Loads the schema.json file."""
    return get_json(get_abs_path("schemas/{}.json".format(entity)))


def write_state(state_values, file_name):
    """Write the state of a stream to the state.json file."""
    fileout = open(get_abs_path(file_name), 'w')
    json.dump(state_values, fileout)
    fileout.close()


def load_tap_setting(path):
    """Loads a .json file using the absolute path."""
    return get_json(get_abs_path(path))


def transform_headers(a_list):
    """Convert to lower case and replace spaces with underscore."""
    key_list = []

    for i in a_list:
        new_k = re.sub(' |-', '_', i.lower())
        key_list.append(new_k)

    return key_list


def transform_type(transform_keys, a_dict, target_type):
    """ Takes a list of keys whose values are to be transformed to
     the target type.

    :param transform_keys: keys; list
    :param a_dict: key values
    :param target_type: transformation target
    :return: dictionary of transformed values
    """
    if target_type == 'int':
        return {
            key: int(
                value) if key in transform_keys and value is not None else value
            for key, value in a_dict.items()}
    elif target_type == 'float':
        return {key: float(
            value) if key in transform_keys and value is not None else value
                for
                key, value in a_dict.items()}
    else:
        print('Invalid target_type argument.')


def data_extraction(data):
    """Takes data from HTTP response and returns the keys and data as a tuple.

    :param data: the HTTP body response
    :return: file headers and data; tuple
    """
    keys = data.split('\n', 1)[0].split('\t')
    keys = transform_headers(keys)
    data_clean = data.split('\n')[1:]

    return keys, data_clean


def get_special_schema_types(schema_properties):
    """ Loops through a schema and returns a dictionary of data names that
    are integers or floats for downstream processing.

    :param schema_properties: the schema to be processed
    :return: dictionary of data names whose values are integers or floats
    """
    number_types = []
    float_types = []

    for k in schema_properties:
        data_values = schema_properties[k]['type']
        if 'number' in data_values:
            float_types.append(k)
        elif 'integer' in data_values:
            number_types.append(k)
        else:
            pass

    types_dict = {'float_keys': float_types, 'int_keys': number_types}

    return types_dict


def process_records(file_header, file_data, n_state, int_keys, float_keys,
                    schema):
    """Write Singer record to stdout.

    :param file_header: file headers
    :param file_data: file data
    :param n_state: date data was fetched for
    :param int_keys: data that should be of type int
    :param float_keys: data that should of type float
    :param schema: data schema being processed; string
    :return: nothing
    """

    for row in file_data:
        if row:
            dat = row.split('\t')
            data_dict = dict(zip(file_header, dat))

            if schema == 'itunes_subscriptions':
                data_dict.update({'date': str(n_state.format('%Y-%m-%d'))})

            for key in data_dict:

                if data_dict[key].strip() == '':
                    data_dict[
                        key] = None

            row_entry = transform_type(int_keys, data_dict, 'int')
            row_entry = transform_type(float_keys, row_entry, 'float')
            singer.write_record(schema, row_entry)


def gen_dates(current_state, state_date_format, time_zone='America/Los_Angeles'):
    """Generates a list of dates.

    :param current_state: current state in %Y-%m-%d format
    :param time_zone: timezone; string
    :param state_date_format: the state date format; string
    :return: list of dates in %Y-%m-%d format
    """

    today_ = pendulum.today(tz=time_zone)
    last_day = pendulum.parse(current_state, tz=time_zone)
    delta = today_ - last_day
    d_days = delta.days

    dates = []

    for i in range(1, d_days):
        dates.append(last_day.add(days=i).format(state_date_format))

    return dates
