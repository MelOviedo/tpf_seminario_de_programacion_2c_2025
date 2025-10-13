from .subtractor import subtract

def divide(A: int, B: int, n_bits: int):
  """
  División entera no signada usando algoritmo restaurador:
    Recorre desde el bit más alto al más bajo del dividendo A.
    En cada paso: R = (R << 1) | bit, y si R >= B entonces R = R - B y Q_i = 1.

  Usa el subtractor con ancho (n_bits + 1) para evitar overflow en el resto intermedio.
  Devuelve (Q, R, net_ultima_resta)
  """
  if B == 0:
    raise ZeroDivisionError('División por cero')

  # Normalizamos A y B al rango de n_bits
  mask_n = (1 << n_bits) - 1
  A &= mask_n
  B &= mask_n

  width = n_bits + 1              # resto puede crecer un bit al desplazar
  mask_w = (1 << width) - 1

  Q = 0
  R = 0
  last_net = None

  # i = n_bits-1 .. 0
  for i in range(n_bits - 1, -1, -1):
    # Traer el bit i de A y "bajarlo" al resto
    bit = (A >> i) & 1
    R = ((R << 1) | bit) & mask_w

    # ¿R >= B? -> usamos subtract para decidir
    val_mod, borrow, net = subtract(R, B, width)  # width = n_bits+1
    last_net = net
    if borrow == 0:           # NO hubo préstamo => R >= B
      R = val_mod             # aceptamos la resta
      Q |= (1 << i)           # seteamos el bit i del cociente

  # R está en [0, B) garantizado
  return Q, R, last_net

from .subtractor import subtract

def divide_with_traces(A: int, B: int, n_bits: int):
  """
  Igual que divide(), pero devuelve además las nets de cada resta aceptada (R>=B).
  """
  if B == 0:
    raise ZeroDivisionError('División por cero')

  mask_n = (1 << n_bits) - 1
  A &= mask_n
  B &= mask_n

  width = n_bits + 1
  mask_w = (1 << width) - 1

  Q = 0
  R = 0
  nets = []

  for i in range(n_bits - 1, -1, -1):
    bit = (A >> i) & 1
    R = ((R << 1) | bit) & mask_w

    val_mod, borrow, net = subtract(R, B, width)  # podés modificar subtract para aceptar record=True si querés
    # Re-ejecutamos con record=True para obtener history:
    from .subtractor import build_subtractor, encode_bits as enc, decode_sum as dec
    net_rec = build_subtractor(width)
    enc(net_rec, 'A', R, width)
    enc(net_rec, 'B', B, width)
    net_rec.run(record=True)

    if borrow == 0:
      R = val_mod
      Q |= (1 << i)
      nets.append(net_rec)  # guardamos solo las restas aceptadas

  return Q, R, nets
