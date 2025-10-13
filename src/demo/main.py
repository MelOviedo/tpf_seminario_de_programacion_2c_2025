import argparse
from ..arith.adder import add

def main():
  parser = argparse.ArgumentParser(description='Demo aritmética con RdP')
  sub = parser.add_subparsers(dest='cmd', required=True)

  p_add = sub.add_parser('add', help='Suma binaria con RdP')
  p_add.add_argument('--bits', type=int, required=True)
  p_add.add_argument('--A', type=lambda x: int(x, 0), required=True, help='Entero, soporta prefijo 0b/0x')
  p_add.add_argument('--B', type=lambda x: int(x, 0), required=True)
  p_add.add_argument('--carry_in', type=int, default=0, choices=[0,1])

  args = parser.parse_args()

  if args.cmd == 'add':
    value, net = add(args.A, args.B, args.bits, carry_in=args.carry_in)
    print(f'A={bin(args.A)} B={bin(args.B)} bits={args.bits} carry_in={args.carry_in}')
    print(f'Resultado: {bin(value)} ({value})')
    # mostrar marcas relevantes
    for i in range(args.bits):
      print(f'S_{i}={net.places[f"S_{i}"].tokens}', end=' ')
    print(f'C_{args.bits}={net.places[f"C_{args.bits}"].tokens}')

if __name__ == '__main__':
  main()
