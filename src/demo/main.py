import argparse
from ..arith.adder import add
from ..arith.subtractor import subtract
from ..arith.multiplier import mul as rdp_mul
from ..arith.divider import divide as rdp_div

def main():
    parser = argparse.ArgumentParser(description='Demo aritmética con Redes de Petri')
    parser.add_argument('--trace', action='store_true', help='Imprimir transiciones disparadas')
    subparsers = parser.add_subparsers(dest='cmd', required=True)

    # add
    p_add = subparsers.add_parser('add', help='Suma binaria con RdP')
    p_add.add_argument('--bits', type=int, required=True)
    p_add.add_argument('--A', type=lambda x: int(x, 0), required=True)
    p_add.add_argument('--B', type=lambda x: int(x, 0), required=True)
    p_add.add_argument('--carry_in', type=int, default=0, choices=[0, 1])

    # sub
    p_sub = subparsers.add_parser('sub', help='Resta binaria con RdP (A - B)')
    p_sub.add_argument('--bits', type=int, required=True)
    p_sub.add_argument('--A', type=lambda x: int(x, 0), required=True)
    p_sub.add_argument('--B', type=lambda x: int(x, 0), required=True)

    # mul
    p_mul = subparsers.add_parser('mul', help='Multiplicación binaria con RdP (A * B)')
    p_mul.add_argument('--bits', type=int, required=True)
    p_mul.add_argument('--A', type=lambda x: int(x, 0), required=True)
    p_mul.add_argument('--B', type=lambda x: int(x, 0), required=True)

    # div
    p_div = subparsers.add_parser('div', help='División binaria con RdP (A / B)')
    p_div.add_argument('--bits', type=int, required=True)
    p_div.add_argument('--A', type=lambda x: int(x, 0), required=True)
    p_div.add_argument('--B', type=lambda x: int(x, 0), required=True)

    args = parser.parse_args()
    print(f'[args] {args}', flush=True)

    if args.cmd == 'add':
        value, net = add(args.A, args.B, args.bits, carry_in=args.carry_in)
        print(f'[ADD] A={bin(args.A)}  B={bin(args.B)}  bits={args.bits}  carry_in={args.carry_in}')
        print(f'Resultado: {bin(value)}  ({value})')
        print('S:', ' '.join(f'S_{i}={net.places[f"S_{i}"].tokens}' for i in range(args.bits)))
        print(f'C_out=C_{args.bits}={net.places[f"C_{args.bits}"].tokens}')

    elif args.cmd == 'sub':
        value, borrow, net = subtract(args.A, args.B, args.bits)
        print(f'[SUB] A={bin(args.A)}  B={bin(args.B)}  bits={args.bits}')
        print(f'Resultado (mod 2^{args.bits}): {bin(value)}  ({value})  borrow={borrow}')
        print('S:', ' '.join(f'S_{i}={net.places[f"S_{i}"].tokens}' for i in range(args.bits)))
        print(f'carry_out=C_{args.bits}={net.places[f"C_{args.bits}"].tokens}  (borrow = NOT carry_out)')

    elif args.cmd == 'mul':
        value, net = rdp_mul(args.A, args.B, args.bits)
        total = 2 * args.bits
        print(f'[MUL] A={bin(args.A)}  B={bin(args.B)}  bits={args.bits}')
        print(f'Resultado: {bin(value)}  ({value})  # usa 2*bits')
        acc_bits = ' '.join(f'ACC_{j}={1 if (value >> j) & 1 else 0}' for j in range(total))
        print('ACC:', acc_bits)

    elif args.cmd == 'div':
        try:
            q, r, net = rdp_div(args.A, args.B, args.bits)
        except ZeroDivisionError as e:
            print('Error: división por cero')
            return
        print(f'[DIV] A={bin(args.A)}  B={bin(args.B)}  bits={args.bits}')
        print(f'Q={bin(q)} ({q})  R={bin(r)} ({r})')
    else:
        parser.print_help()

if __name__ == '__main__':
    main()