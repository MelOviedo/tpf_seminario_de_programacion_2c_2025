from .adder import add  # reutiliza el sumador probado

def mul(A: int, B: int, n_bits: int):
  """
  Multiplica A*B usando sumas parciales con el adder de 2*n_bits.
  Resultado y carry viven en 2*n_bits (producto modular en ese ancho).
  Devuelve (producto, net_ultima_suma)
  """
  total_bits = 2 * n_bits     # Para evitar overflow
  acc = 0                     # Acumulador del producto donde se irá sumando el parcial
  last_net = None

  for i in range(n_bits):
    if (B >> i) & 1:
      parcial = (A << i) & ((1 << total_bits) - 1)    # Genera la suma parcial desplazada. Desplaza A i bits a la izquierda
      acc, last_net = add(acc, parcial, total_bits)   # cada suma es una RdP independiente

  return acc, last_net

from .adder import build_adder, encode_bits as enc, decode_sum as dec

def mul_with_traces(A: int, B: int, n_bits: int):
  """
  Devuelve (producto, [nets_por_cada_suma_parcial])
  Cada net es un adder de 2*n_bits con history grabada.
  """
  total_bits = 2 * n_bits
  mask = (1 << total_bits) - 1
  acc = 0
  nets = []

  for i in range(n_bits):
    if (B >> i) & 1:
      parcial = (A << i) & mask
      net = build_adder(total_bits, carry_in=0)
      enc(net, 'A', acc, total_bits)      # acumulador actual
      enc(net, 'B', parcial, total_bits)  # parcial desplazado
      net.run(record=True)
      acc = dec(net, total_bits)
      nets.append(net)

  return acc, nets
