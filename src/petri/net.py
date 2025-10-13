# /src/petri/net.py
from .place import Place
from .transition import Transition

class PetriNet:
  def __init__(self, name='net'):
    self.name = name
    self.places = {}
    self.transitions = []
    self.last_trace = []
    self.initial_marking = None
    self.history = []  # [{'fired': name, 'marking': {place:tokens}}, ...]

  def add_place(self, name, capacity=1, tokens=0):
    if name in self.places:
      raise ValueError(f'La plaza {name} ya existe')
    self.places[name] = Place(name, capacity, tokens)
    return self.places[name]

  def get_place(self, name):
    return self.places[name]

  def add_transition(self, name, inputs=None, outputs=None, guard=None):
    t = Transition(name, inputs, outputs, guard)
    self.transitions.append(t)
    return t

  def enabled_transitions(self):
    return [t for t in self.transitions if t.is_enabled(self)]

  def snapshot(self):
    return {n: p.tokens for n, p in self.places.items()}

  def run(self, max_steps=10_000, record=False):
    steps = 0
    fired = []
    if record:
      self.initial_marking = self.snapshot()
      self.history = []

    while steps < max_steps:
      enabled = self.enabled_transitions()
      if not enabled:
        break
      t = enabled[0]
      t.fire(self)
      fired.append(t.name)
      if record:
        self.history.append({'fired': t.name, 'marking': self.snapshot()})
      steps += 1

    self.last_trace = fired
    return fired
