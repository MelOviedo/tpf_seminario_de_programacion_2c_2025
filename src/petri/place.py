class Place:
  def __init__(self, name, capacity=1, tokens=0):
    self.name = name
    self.capacity = capacity
    self.tokens = int(tokens)

  def can_consume(self, k=1):
    return self.tokens >= k

  def consume(self, k=1):
    if k < 0:
      raise ValueError('k debe ser >= 0')
    if not self.can_consume(k):
      raise RuntimeError(f'No hay tokens suficientes en {self.name}')
    self.tokens -= k

  def produce(self, k=1):
    if k < 0:
      raise ValueError('k debe ser >= 0')
    if self.capacity is not None and self.tokens + k > self.capacity:
      raise RuntimeError(f'Capacidad excedida en {self.name}')
    self.tokens += k

  def __repr__(self):
    cap = '∞' if self.capacity is None else self.capacity
    return f'Place({self.name}, tokens={self.tokens}, cap={cap})'
