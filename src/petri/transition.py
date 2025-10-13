class Transition:
  def __init__(self, name, inputs=None, outputs=None, guard=None):
    self.name = name
    self.inputs = inputs or {}
    self.outputs = outputs or {}
    self.guard = guard  # guard(net) -> bool

  def is_enabled(self, net):
    # 1) tokens suficientes en entradas
    for p, w in self.inputs.items():
      if net.places[p].tokens < w:
        return False
    # 2) guard opcional
    if self.guard is not None and not self.guard(net):
      return False
    return True

  def fire(self, net):
    if not self.is_enabled(net):
      raise RuntimeError(f'Transición no habilitada: {self.name}')
    for p, w in self.inputs.items():
      net.places[p].consume(w)
    for p, w in self.outputs.items():
      net.places[p].produce(w)

  def __repr__(self):
    return f'Transition({self.name})'
