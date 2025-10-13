from ..petri.net import PetriNet

def _bit(value, i):
  return (value >> i) & 1

def encode_bits(net, prefix, value, n_bits):
  for i in range(n_bits):
    net.places[f'{prefix}_{i}'].tokens = 1 if _bit(value, i) else 0

def decode_product(net, n_bits):
  total_bits = 2 * n_bits
  acc = 0
  for j in range(total_bits):
    if net.places[f'ACC_{j}'].tokens > 0:
      acc |= (1 << j)
  return acc

def build_multiplier(n_bits):
  total_bits = 2 * n_bits
  net = PetriNet('multiplier')

  # Entradas
  for i in range(n_bits):
    net.add_place(f'A_{i}', capacity=1, tokens=0)
    net.add_place(f'B_{i}', capacity=1, tokens=0)

  # Acumulador (resultado) y buffer de suma
  for j in range(total_bits):
    net.add_place(f'ACC_{j}', capacity=1, tokens=0)
    net.add_place(f'S_{j}', capacity=1, tokens=0)

  # Carry/etapas del adder interno
  for j in range(total_bits + 1):
    net.add_place(f'C_{j}', capacity=1, tokens=0)
    net.add_place(f'STAGE_{j}', capacity=1, tokens=0)

  # Etapas de commit S -> ACC
  for j in range(total_bits + 1):
    net.add_place(f'COMMIT_{j}', capacity=1, tokens=0)

  # Control externo sobre bits de B
  for i in range(n_bits + 1):
    net.add_place(f'OUTER_{i}', capacity=1, tokens=0)
  net.places['OUTER_0'].tokens = 1

  def has(p):
    return net.places[p].tokens > 0

  # Recorrer bits de B
  for i in range(n_bits):
    Bi = f'B_{i}'

    # Si B_i == 0 → saltar
    def g_skip(net, Bi=Bi):
      return not has(Bi)
    net.add_transition(
      name=f'MUL{i}_SKIP',
      inputs={f'OUTER_{i}': 1},
      outputs={f'OUTER_{i+1}': 1},
      guard=g_skip
    )

    # Si B_i == 1 → iniciar adder interno
    def g_start_add(net, Bi=Bi):
      return has(Bi)
    net.add_transition(
      name=f'MUL{i}_START_ADD',
      inputs={f'OUTER_{i}': 1},
      outputs={'STAGE_0': 1},
      guard=g_start_add
    )

    # Adder interno (ripple) para sumar A<<i a ACC
    for j in range(2 * n_bits):
      Ci, Co = f'C_{j}', f'C_{j+1}'
      St, Stn = f'STAGE_{j}', f'STAGE_{j+1}'
      Sj = f'S_{j}'
      ACCj = f'ACC_{j}'

      # p_j = (B_i & A_{j-i}) si cae en rango [0, n_bits)
      def p_one(net, i=i, j=j, n=n_bits):
        if not has(f'B_{i}'):
          return False
        k = j - i
        return 0 <= k < n and has(f'A_{k}')

      def acc_one(net, ACCj=ACCj):
        return has(ACCj)

      # ci=0
      def g_ci0_eq00(net, Ci=Ci):
        return not has(Ci) and (not p_one(net)) and (not acc_one(net))
      net.add_transition(f'MUL{i}_{j}_ci0_eq00', {St: 1}, {Stn: 1}, g_ci0_eq00)

      def g_ci0_eq11(net, Ci=Ci):
        return not has(Ci) and p_one(net) and acc_one(net)
      net.add_transition(f'MUL{i}_{j}_ci0_eq11', {St: 1}, {Stn: 1, Co: 1}, g_ci0_eq11)

      def g_ci0_xor(net, Ci=Ci):
        return not has(Ci) and (p_one(net) != acc_one(net))
      net.add_transition(f'MUL{i}_{j}_ci0_xor', {St: 1}, {Stn: 1, Sj: 1}, g_ci0_xor)

      # ci=1
      def g_ci1_xor(net, Ci=Ci):
        return has(Ci) and (p_one(net) != acc_one(net))
      net.add_transition(f'MUL{i}_{j}_ci1_xor', {St: 1, Ci: 1}, {Stn: 1, Co: 1}, g_ci1_xor)

      def g_ci1_eq00(net, Ci=Ci):
        return has(Ci) and (not p_one(net)) and (not acc_one(net))
      net.add_transition(f'MUL{i}_{j}_ci1_eq00', {St: 1, Ci: 1}, {Stn: 1, Sj: 1}, g_ci1_eq00)

      def g_ci1_eq11(net, Ci=Ci):
        return has(Ci) and p_one(net) and acc_one(net)
      net.add_transition(f'MUL{i}_{j}_ci1_eq11', {St: 1, Ci: 1}, {Stn: 1, Sj: 1, Co: 1}, g_ci1_eq11)

    # Fin del adder -> pasar a commit (consumiendo STAGE_total y opcionalmente C_total)
    def g_carry_absent(net, idx=2 * n_bits):
      return not has(f'C_{idx}')
    net.add_transition(f'MUL{i}_TO_COMMIT_NO_COUT', {f'STAGE_{2*n_bits}': 1}, {'COMMIT_0': 1}, g_carry_absent)

    def g_carry_present(net, idx=2 * n_bits):
      return has(f'C_{idx}')
    net.add_transition(f'MUL{i}_TO_COMMIT_WITH_COUT', {f'STAGE_{2*n_bits}': 1, f'C_{2*n_bits}': 1}, {'COMMIT_0': 1}, g_carry_present)

    # Commit: copiar S -> ACC y limpiar S
    for j in range(2 * n_bits):
      CSt, CStn = f'COMMIT_{j}', f'COMMIT_{j+1}'
      Sj, ACCj = f'S_{j}', f'ACC_{j}'

      def g_set1(net, Sj=Sj, ACCj=ACCj):
        return has(Sj) and not has(ACCj)
      net.add_transition(
        f'COMMIT{i}_{j}_set1',
        {CSt: 1, Sj: 1},
        {CStn: 1, ACCj: 1}
      )

      def g_keep1(net, Sj=Sj, ACCj=ACCj):
        return has(Sj) and has(ACCj)
      net.add_transition(f'COMMIT{i}_{j}_keep1', {CSt: 1, Sj: 1}, {CStn: 1})

      def g_set0(net, Sj=Sj, ACCj=ACCj):
        return (not has(Sj)) and has(ACCj)
      net.add_transition(f'COMMIT{i}_{j}_set0', {CSt: 1, ACCj: 1}, {CStn: 1})

      def g_keep0(net, Sj=Sj, ACCj=ACCj):
        return (not has(Sj)) and (not has(ACCj))
      net.add_transition(f'COMMIT{i}_{j}_keep0', {CSt: 1}, {CStn: 1}, g_keep0)

    # Fin de commit -> avanzar OUTER
    net.add_transition(f'COMMIT{i}_DONE', {f'COMMIT_{2*n_bits}': 1}, {f'OUTER_{i+1}': 1})

  return net

def mul(A, B, n_bits):
  net = build_multiplier(n_bits)
  encode_bits(net, 'A', A, n_bits)
  encode_bits(net, 'B', B, n_bits)
  net.run()
  return decode_product(net, n_bits), net