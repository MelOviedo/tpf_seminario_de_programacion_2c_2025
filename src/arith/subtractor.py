from ..petri.net import PetriNet
from .adder import build_adder, encode_bits, decode_sum

def build_subtractor(n_bits):
  """
  Construye una red que computa A - B usando A + (~B + 1).
  Reutiliza el sumador ripple-carry (carry_in=1) y agrega una fase previa
  que invierte cada bit de B dentro de la propia RdP (NOT bit a bit).

  Convenciones de plazas del adder:
    A_i, B_i, S_i, C_0..C_n, STAGE_0..STAGE_n
  Se agregan: NEG_STAGE_0..NEG_STAGE_n para recorrer y hacer NOT(B)
  """
  # 1) Crear el sumador con carry_in=1
  net = build_adder(n_bits, carry_in=1)

  # 2) Anular el arranque automático del sumador: primero hacemos NOT(B)
  net.places['STAGE_0'].tokens = 0

  # 3) Crear la "pipeline" de negación de B
  for i in range(n_bits + 1):
    net.add_place(f'NEG_STAGE_{i}', capacity=1, tokens=0)
  net.places['NEG_STAGE_0'].tokens = 1

  def has(p):
    return net.places[p].tokens > 0

  for i in range(n_bits):
    Bi = f'B_{i}'
    NSi, NSn = f'NEG_STAGE_{i}', f'NEG_STAGE_{i+1}'

    # Si B_i == 1: consumir el 1 → deja 0
    def g_has1(net, Bi=Bi):
      return has(Bi)

    net.add_transition(
      name=f'NEG{i}_one_to_zero',
      inputs={NSi: 1, Bi: 1},
      outputs={NSn: 1},
      guard=g_has1
    )

    # Si B_i == 0: producir un 1 en B_i
    def g_has0(net, Bi=Bi):
      return not has(Bi)

    net.add_transition(
      name=f'NEG{i}_zero_to_one',
      inputs={NSi: 1},
      outputs={NSn: 1, Bi: 1},
      guard=g_has0
    )

  # 4) Al terminar la negación, habilitar la etapa 0 del sumador
  net.add_transition(
    name='NEG_DONE_START_ADD',
    inputs={f'NEG_STAGE_{n_bits}': 1},
    outputs={'STAGE_0': 1}
  )

  return net

def subtract(A, B, n_bits):
  """
  Devuelve (resultado_mod_2^n, borrow_flag, net)
  borrow_flag = 0 si NO hubo préstamo (C_n=1), 1 si hubo préstamo (C_n=0)
  """
  net = build_subtractor(n_bits)
  encode_bits(net, 'A', A, n_bits)
  encode_bits(net, 'B', B, n_bits)   # se invierte dentro de la red
  net.run()

  value = decode_sum(net, n_bits)     # decodifica S_0..S_{n-1} y C_n como bit extra
  mask = (1 << n_bits) - 1
  value_mod = value & mask

  # En resta por complemento-2: borrow = NOT carry_out
  carry_out = 1 if net.places[f'C_{n_bits}'].tokens > 0 else 0
  borrow = 0 if carry_out == 1 else 1

  return value_mod, borrow, net
