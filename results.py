#!/usr/bin/env python3

import csv
import sys
import json

from argparse import ArgumentParser
from collections import namedtuple
from collections import OrderedDict

car_lookup = {
  0: 'Porsche 991 GT3 R',
  1: 'Mercedes-AMG GT3',
  2: 'Ferrari 488 GT3',
  3: 'Audi R8 LMS',
  4: 'Lamborghini Huracan GT3',
  5: 'McLaren 650S GT3',
  6: 'Nissan GT-R Nismo GT3',
  7: 'BMW M6 GT3',
  8: 'Bentley Continental GT3',
  9: 'Porsche 991 II GT3 Cup',
  10: 'Nissan GT-R Nismo GT3',
  11: 'Bentley Continental GT3',
  12: 'AMR V12 Vantage GT3',
  13: 'Reiter Engineering R-EX GT3',
  14: 'Emil Frey Jaguar G3',
  15: 'Lexus RC F GT3',
  16: 'Lamborghini Huracan GT3 Evo',
  17: 'Honda NSX GT3',
  18: 'Lamborghini Huracan SuperTrofeo',
  19: 'Audi R8 LMS Evo',
  20: 'AMR V8 Vantage',
  21: 'Honda NSX GT3 Evo',
  22: 'McLaren 720S GT3',
  23: 'Porsche 911 II GT3 R',
  24: 'Ferrari 488 GT3 Evo',
  25: 'Mercedes-AMG GT3',
  26: 'Ferrari 488 Challenge Evo',
  27: 'BMW M2 CS Racing',
  28: 'Porsche 911 GT3 Cup (Type 992)',
  29: 'Lamborghini Huracán Super Trofeo EVO2',
  30: 'BMW M4 GT3',
  31: 'Audi R8 LMS GT3 evo II',
  50: 'Alpine A110 GT4',
  51: 'Aston Martin GT4',
  52: 'Audi R8 LMS GT4',
  53: 'BMW M4 GT4',
  55: 'Chevrolet Camaro GT4',
  56: 'Ginetta G55 GT4',
  57: 'KTM X-Bow GT4',
  58: 'Maserati MC GT4',
  59: 'McLaren 570S GT4',
  60: 'Mercedes AMG GT4',
  61: 'Porsche Cayman GT4'
}

LapEntry = namedtuple('LapEntry', ('driver', 'car', 'laptime', 'splits'))

laps = []

key_funcs = {
  'car':        lambda lap: lap.car,
  'driver':     lambda lap: lap.driver,
  'car_driver': lambda lap: (lap.driver, lap.car)
}

argparser = ArgumentParser()
argparser.add_argument('--by', choices=key_funcs.keys(), default='car_driver')
argparser.add_argument('--sectors', action='store_true')
argparser.add_argument('--csv')
argparser.add_argument('file', nargs='+')

args = argparser.parse_args(sys.argv[1:])

key_func = key_funcs[args.by]

for fn in args.file:
  with open(fn, encoding='utf-16le') as f:
    d = json.load(f)
    leaderboard = d['sessionResult']['leaderBoardLines']
    for entry in leaderboard:
      driver = entry['currentDriver']['firstName'].strip() + ' ' + entry['currentDriver']['lastName'].strip()
      car = car_lookup[entry['car']['carModel']]
      splits = [s / 1000 for s in entry['timing']['bestSplits']]
      lap_time = entry['timing']['bestLap'] / 1000
      if lap_time < 2147483.647:
        laps.append(LapEntry(driver, car, lap_time, splits))

laps = sorted(laps, key=lambda e: e.laptime)

driver_car_laps = OrderedDict()

for l in laps:
  key = key_func(l)
  if not key in driver_car_laps:
    driver_car_laps[key] = l

def format_time(t):
  m = int(t / 60)
  s = int(t % 60)
  ms = int((t * 1000) % 1000)
  if m > 0:
    return f'{m:02}:{s:02}:{ms:03}'
  else:
    return f'{s:02}:{ms:03}'

def format_time_csv(t):
  m = int(t / 60)
  s = int(t % 60)
  ms = int((t * 1000) % 1000)
  return f'00:{m:02}:{s:02}.{ms:03}'

for l in driver_car_laps.values():
  laptime = format_time(l.laptime)
  s = f'{l.driver:30} {l.car:25} {laptime}'
  if args.sectors:
    splits = '  '.join((format_time(s) for s in l.splits))
    s += '      ' + splits
  print(s)

if args.csv:
  with open(args.csv, 'w') as f:
    writer = csv.writer(f)
    for l in driver_car_laps.values():
      writer.writerow((l.driver, l.car, format_time_csv(l.laptime)))
