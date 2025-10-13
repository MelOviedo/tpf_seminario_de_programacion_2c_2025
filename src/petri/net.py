from .place import Place
from .transition import Transition

class PetriNet:
  def __init__(self, name='net'):
    self.name = name
    self.places = {}
    self.transitions = []
    self.last_trace = []

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

  def run(self, max_steps=10_000):
    steps = 0
    fired = []
    while steps < max_steps:
      enabled = self.enabled_transitions()
      if not enabled:
        break
      # política simple: tomar la primera habilitada
      t = enabled[0]
      t.fire(self)
      fired.append(t.name)
      steps += 1
    self.last_trace = fired
    return fired
