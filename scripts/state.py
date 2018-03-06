#!/usr/bin/python2
# Author: Rustam Gubaydullin (@second_fry)
# License: MIT (https://opensource.org/licenses/MIT)

from copy import deepcopy
import json


class State(object):
  def __init__(self, path, default):
    self.path = path
    self.default = default
    self._read()

  def _read(self):
    try:
      with open(self.path, 'r') as f:
        self.state = json.load(f)
    except:
      self._default()

  def _default(self):
    self.state = deepcopy(self.default)

  def _write(self):
    with open(self.path, 'w') as f:
      f.write(json.dumps(self.state))

  def set(self, key, val):
    self.state[key] = val
    return self

  def get(self, key):
    return self.state[key]

  def increment(self, key):
    self.state[key] += 1
    return self

  def decrement(self, key):
    self.state[key] -= 1
    return self

  def save(self):
    self._write()
