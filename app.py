#!/usr/bin/env python

import argparse
import json
import datetime
import requests
import psycopg2
import uuid


def _check_value(value):
    if value == '.':
        return None
    else:
        return float(value)


def _main(args):
    batch_size = args.batch_size
    config = None
    params = dict([('api_key', None), ('series_id', None), ('file_type', None), ('observation_start', None), ('observation_end', None)])

    with open(args.config, 'r') as file:
        print('Loading configuration file...')
        config = json.load(file)

    params['api_key'] = config['api_key']
    params['file_type'] = config['file_type']
    params['observation_start'] = args.obs_start
    params['observation_end'] = args.obs_end
    params['realtime_start'] = args.real_start
    params['realtime_end'] = args.real_end

    url = "{protocol}://{host}{endpoint}".format(protocol=config['protocol'], host=config['host'], endpoint=config['endpoints']['observations'])

    try:
        conn = psycopg2.connect(dbname="fred", user="saintlouis", password="econ", host="127.0.0.1", port=5432)
        cur = conn.cursor()

        for series_id in config['series']:
            params['series_id'] = series_id
            print('Fetching data...')
            resp = requests.get(url, params=params)
            if resp.status_code >= 400:
                msg = resp.json()['error_message']
                raise Exception(msg)
            data = resp.json()
            observations = data['observations']
            print("Fetched {} data observations...".format(len(observations)))

            batchs = len(observations) // batch_size
            for batch_cnt in range(batchs):
                batch = []
                
                if batch_cnt == (batchs - 1):
                    batch = observations[(batch_cnt * batch_size):]
                else:
                    batch = observations[(batch_cnt * batch_size):((batch_cnt + 1) * batch_size)]

                vals = [(str(uuid.uuid4()), row['realtime_start'], row['realtime_end'], row['date'], _check_value(row['value'])) for row in batch]
                val_stmt = ','.join(cur.mogrify('(%s,%s,%s,%s,%s)', val).decode('UTF-8') for val in vals)
                sql_stmt = "insert into economics.{table} values {values}".format(table=series_id.lower(), values=val_stmt)
                cur.execute(sql_stmt)
                conn.commit()
                print('Saving batch...')

    except Exception as error:
        print(error)

    finally:
        conn.close()
        print('ETL complete.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='FRED')
    parser.add_argument('--obs_start', action='store', default='1776-07-04', type=str)
    parser.add_argument('--obs_end', action='store', default='9999-12-31', type=str)
    parser.add_argument('--real_start', action='store')
    parser.add_argument('--real_end', action='store')
    parser.add_argument('--batch_size', action='store', default=100, type=int)
    parser.add_argument('config')
    args = parser.parse_args()

    if args.real_start is None or args.real_end is None:
        today = datetime.date.today().strftime('%Y-%m-%d')
        args.real_start = today
        args.real_end = today

    _main(args)
