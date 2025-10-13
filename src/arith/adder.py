from ..petri.net import PetriNet

def _bit(value, i):
  return (value >> i) & 1

def encode_bits(net, prefix, value, n_bits):
  for i in range(n_bits):
    place = f'{prefix}_{i}'
    net.places[place].tokens = 1 if _bit(value, i) else 0

def decode_sum(net, n_bits):
  acc = 0
  for i in range(n_bits):
    if net.places[f'S_{i}'].tokens > 0:
      acc |= (1 << i)
  if net.places[f'C_{n_bits}'].tokens > 0:
    acc |= (1 << n_bits)
  return acc

def build_adder(n_bits, carry_in=0):
  """
  Sumador ripple-carry con 8 transiciones por bit (todas consumen STAGE_i).
  Casos cubiertos (Ai,Bi,Ci):
    ci=0: eq00 -> s=0,co=0 | eq11 -> s=0,co=1 | xor -> s=1,co=0
    ci=1: xor  -> s=0,co=1 | eq00-> s=1,co=0 | eq11-> s=1,co=1
  """
  if carry_in not in (0, 1):
    raise ValueError('carry_in debe ser 0 o 1')

  net = PetriNet('adder')

  # Plazas de datos
  for i in range(n_bits):
    net.add_place(f'A_{i}', capacity=1, tokens=0)
    net.add_place(f'B_{i}', capacity=1, tokens=0)
    net.add_place(f'S_{i}', capacity=1, tokens=0)

  # Carries C_0..C_n
  for i in range(n_bits + 1):
    net.add_place(f'C_{i}', capacity=1, tokens=0)

  # Control STAGE_0..STAGE_n
  for i in range(n_bits + 1):
    net.add_place(f'STAGE_{i}', capacity=1, tokens=0)

  # Inicialización
  net.places['STAGE_0'].tokens = 1
  net.places['C_0'].tokens = carry_in

  def has(p):  # lector de tokens (guard)
    return net.places[p].tokens > 0

  for i in range(n_bits):
    Ai, Bi = f'A_{i}', f'B_{i}'
    Ci, Co = f'C_{i}', f'C_{i+1}'
    Si = f'S_{i}'
    St, Stn = f'STAGE_{i}', f'STAGE_{i+1}'

    # --- ci = 0 ---
    def g_ci0_eq00(net, Ai=Ai, Bi=Bi, Ci=Ci):
      return (not has(Ci)) and (not has(Ai)) and (not has(Bi))
    net.add_transition(
      name=f'T{i}_ci0_eq00',
      inputs={St:1},
      outputs={Stn:1},
      guard=g_ci0_eq00
    )

    def g_ci0_eq11(net, Ai=Ai, Bi=Bi, Ci=Ci):
      return (not has(Ci)) and has(Ai) and has(Bi)
    net.add_transition(
      name=f'T{i}_ci0_eq11',
      inputs={St:1},
      outputs={Stn:1, Co:1},
      guard=g_ci0_eq11
    )

    def g_ci0_xor(net, Ai=Ai, Bi=Bi, Ci=Ci):
      return (not has(Ci)) and (has(Ai) != has(Bi))
    net.add_transition(
      name=f'T{i}_ci0_xor',
      inputs={St:1},
      outputs={Stn:1, Si:1},
      guard=g_ci0_xor
    )

    # --- ci = 1 ---
    def g_ci1_xor(net, Ai=Ai, Bi=Bi, Ci=Ci):
      return has(Ci) and (has(Ai) != has(Bi))
    net.add_transition(
      name=f'T{i}_ci1_xor',
      inputs={St:1, Ci:1},
      outputs={Stn:1, Co:1},
      guard=g_ci1_xor
    )

    def g_ci1_eq00(net, Ai=Ai, Bi=Bi, Ci=Ci):
      return has(Ci) and (not has(Ai)) and (not has(Bi))
    net.add_transition(
      name=f'T{i}_ci1_eq00',
      inputs={St:1, Ci:1},
      outputs={Stn:1, Si:1},
      guard=g_ci1_eq00
    )

    def g_ci1_eq11(net, Ai=Ai, Bi=Bi, Ci=Ci):
      return has(Ci) and has(Ai) and has(Bi)
    net.add_transition(
      name=f'T{i}_ci1_eq11',
      inputs={St:1, Ci:1},
      outputs={Stn:1, Si:1, Co:1},
      guard=g_ci1_eq11
    )

  return net

def add(A, B, n_bits, carry_in=0):
  net = build_adder(n_bits, carry_in=carry_in)
  encode_bits(net, 'A', A, n_bits)
  encode_bits(net, 'B', B, n_bits)
  net.run()
  return decode_sum(net, n_bits), net