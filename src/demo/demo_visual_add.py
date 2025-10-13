# demo_visual_add.py (ejemplo suelto o en un notebook)
from src.arith.adder import build_adder, encode_bits, decode_sum
from src.petri.viz import render_history_svgs, make_gif_from_svgs

# Construyo red 4 bits
net = build_adder(4, carry_in=0)
encode_bits(net, 'A', 0b1011, 4)
encode_bits(net, 'B', 0b0101, 4)

# Correr grabando la historia
net.run(record=True)

# Exportar frames SVG y GIF
svgs = render_history_svgs(net, out_dir='out/add_1011_0101')
gif = make_gif_from_svgs(svgs, out_gif='out/add_1011_0101.gif')
print('Listo:', gif)
