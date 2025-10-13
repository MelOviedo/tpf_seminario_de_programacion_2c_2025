import argparse
from pathlib import Path

# ADDER
from src.arith.adder import build_adder, encode_bits as enc_add, decode_sum as dec_add
# SUBTRACTOR (ojo: encode/decode se importan del adder)
from src.arith.subtractor import build_subtractor
# MULTIPLIER (usa versión con trazas por sumas parciales)
from src.arith.multiplier import mul_with_traces
# DIVIDER (usa versión con trazas por restas aceptadas)
from src.arith.divider import divide_with_traces

from src.petri.viz import render_history_frames, make_gif_from_frames

def op_add(bits, A, B, outdir, prefix, carry_in):
  net = build_adder(bits, carry_in=carry_in)
  enc_add(net, 'A', A, bits)
  enc_add(net, 'B', B, bits)
  net.run(record=True)
  out = Path(outdir) / prefix
  frames = render_history_frames(net, out_dir=str(out), fmt='png')
  make_gif_from_frames(frames, out_gif=str(out) + '.gif')
  value = dec_add(net, bits)
  print(f'[ADD] A={bin(A)} B={bin(B)} bits={bits} -> {bin(value)} ({value})')
  print(f'Frames: {len(frames)}  GIF: {out}.gif')

def op_sub(bits, A, B, outdir, prefix):
  net = build_subtractor(bits)
  enc_add(net, 'A', A, bits)
  enc_add(net, 'B', B, bits)
  net.run(record=True)
  out = Path(outdir) / prefix
  frames = render_history_frames(net, out_dir=str(out), fmt='png')
  make_gif_from_frames(frames, out_gif=str(out) + '.gif')
  value = dec_add(net, bits)
  carry_out = net.places[f'C_{bits}'].tokens
  borrow = 0 if carry_out == 1 else 1
  print(f'[SUB] A={bin(A)} B={bin(B)} bits={bits} -> {bin(value)} ({value}), borrow={borrow}')
  print(f'Frames: {len(frames)}  GIF: {out}.gif')

def op_mul(bits, A, B, outdir, prefix):
  prod, nets = mul_with_traces(A, B, bits)
  print(f'[MUL] A={bin(A)} B={bin(B)} bits={bits} -> {bin(prod)} ({prod})')
  for k, net in enumerate(nets):
    out = Path(outdir) / f'{prefix}_step{k}'
    frames = render_history_frames(net, out_dir=str(out), fmt='png')
    make_gif_from_frames(frames, out_gif=str(out) + '.gif')
    print(f'  · Paso {k}: frames={len(frames)}  GIF: {out}.gif')
  if not nets:
    print('  · No hubo sumas parciales (B==0)')

def op_div(bits, A, B, outdir, prefix):
  q, r, nets = divide_with_traces(A, B, bits)
  print(f'[DIV] A={bin(A)} B={bin(B)} bits={bits} -> Q={bin(q)} ({q}), R={bin(r)} ({r})')
  for k, net in enumerate(nets):
    out = Path(outdir) / f'{prefix}_step{k}'
    frames = render_history_frames(net, out_dir=str(out), fmt='png')
    make_gif_from_frames(frames, out_gif=str(out) + '.gif')
    print(f'  · Resta aceptada {k}: frames={len(frames)}  GIF: {out}.gif')
  if not nets:
    print('  · No hubo restas aceptadas (A < B)')

def main():
  p = argparse.ArgumentParser(description='Visualizador de Redes de Petri (GIF/SVG) para add/sub/mul/div')
  sub = p.add_subparsers(dest='cmd', required=True)

  def add_common(sp):
    sp.add_argument('--bits', type=int, required=True)
    sp.add_argument('--A', type=lambda x: int(x, 0), required=True)
    sp.add_argument('--B', type=lambda x: int(x, 0), required=True)
    sp.add_argument('--outdir', default='out')
    sp.add_argument('--prefix', default=None)

  sp_add = sub.add_parser('add', help='Suma')
  add_common(sp_add)
  sp_add.add_argument('--carry_in', type=int, default=0, choices=[0, 1])

  sp_sub = sub.add_parser('sub', help='Resta (complemento a 2)')
  add_common(sp_sub)

  sp_mul = sub.add_parser('mul', help='Multiplicación (sumas parciales)')
  add_common(sp_mul)

  sp_div = sub.add_parser('div', help='División (restaurador)')
  add_common(sp_div)

  args = p.parse_args()
  prefix = args.prefix or f'{args.cmd}_{args.A}_{args.B}_b{args.bits}'

  if args.cmd == 'add':
    op_add(args.bits, args.A, args.B, args.outdir, prefix, args.carry_in)
  elif args.cmd == 'sub':
    op_sub(args.bits, args.A, args.B, args.outdir, prefix)
  elif args.cmd == 'mul':
    op_mul(args.bits, args.A, args.B, args.outdir, prefix)
  elif args.cmd == 'div':
    op_div(args.bits, args.A, args.B, args.outdir, prefix)

if __name__ == '__main__':
  main()
