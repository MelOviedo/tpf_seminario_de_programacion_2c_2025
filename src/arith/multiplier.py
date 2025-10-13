from .adder import add  # reutiliza el sumador probado

def mul(A: int, B: int, n_bits: int):
  """
  Multiplica A*B usando sumas parciales con el adder de 2*n_bits.
  Resultado y carry viven en 2*n_bits (producto modular en ese ancho).
  Devuelve (producto, net_ultima_suma)
  """
  total_bits = 2 * n_bits
  acc = 0
  last_net = None

  for i in range(n_bits):
    if (B >> i) & 1:
      parcial = (A << i) & ((1 << total_bits) - 1)
      acc, last_net = add(acc, parcial, total_bits)  # cada suma es una RdP independiente

  return acc, last_net
