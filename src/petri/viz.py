# src/petri/viz.py
from graphviz import Digraph
from pathlib import Path
import imageio.v2 as imageio

def net_to_graph(net, highlight_enabled=True, fired=None, rankdir='LR'):
  """
  Devuelve un Digraph de Graphviz para el net actual.
  - highlight_enabled: pinta de verde transiciones habilitadas
  - fired: nombre de transición disparada (resalta en dorado)
  """
  g = Digraph('petri')
  g.attr(rankdir=rankdir, fontsize='10')

  # Lugares (IDs sin ':')
  for name, place in net.places.items():
    pid = f'p__{name}'
    label = f'{name}\n{place.tokens}/{place.capacity if place.capacity is not None else "∞"}'
    filled = place.tokens > 0
    g.node(pid,
           label=label,
           shape='circle',
           style='filled' if filled else 'solid',
           fillcolor='lightgray' if filled else 'white')

  # Transiciones (IDs sin ':')
  for t in net.transitions:
    tid = f't__{t.name}'
    enabled = t.is_enabled(net)
    style = 'filled' if (highlight_enabled and enabled) or (fired and t.name == fired) else 'solid'
    fill = ('gold' if fired and t.name == fired
            else ('palegreen' if highlight_enabled and enabled else 'white'))
    g.node(tid, label=t.name, shape='box', style=style, fillcolor=fill)

    # Arcos
    for p, w in t.inputs.items():
      g.edge(f'p__{p}', tid, label='' if w == 1 else str(w))
    for p, w in t.outputs.items():
      g.edge(tid, f'p__{p}', label='' if w == 1 else str(w))

  return g

def _save_frame(net, out_path, fired=None, fmt='png'):
  """
  Renderiza un frame (PNG por defecto) y devuelve la ruta del archivo.
  out_path: ruta base sin extensión (p.ej. out/frame_001)
  """
  g = net_to_graph(net, fired=fired)
  out = Path(out_path)
  out.parent.mkdir(parents=True, exist_ok=True)
  g.format = fmt
  # graphviz genera out.stem + '.' + fmt
  g.render(filename=out.stem, directory=str(out.parent), cleanup=True)
  return str(out.with_suffix(f'.{fmt}'))

def render_history_frames(net, out_dir, fmt='png'):
  """
  Dibuja:
  - frame_000: estado inicial (si net.run(record=True) guardó initial_marking)
  - frame_k: tras cada disparo (resaltando la transición 'fired')
  Devuelve lista de rutas a los frames (PNG por defecto).
  """
  out = Path(out_dir)
  out.mkdir(parents=True, exist_ok=True)

  frames = []
  # Guardar el estado actual para restaurar al final
  current = {n: p.tokens for n, p in net.places.items()}

  # Frame inicial
  if getattr(net, 'initial_marking', None):
    for n, tok in net.initial_marking.items():
      net.places[n].tokens = tok
    frames.append(_save_frame(net, out / 'frame_000', fmt=fmt))

  # Frames por paso (aplicamos el marcado del snapshot guardado en history)
  for idx, step in enumerate(getattr(net, 'history', []), start=1):
    for n, tok in step['marking'].items():
      net.places[n].tokens = tok
    frames.append(_save_frame(net, out / f'frame_{idx:03d}', fired=step['fired'], fmt=fmt))

  # Restaurar estado original
  for n, tok in current.items():
    net.places[n].tokens = tok

  return frames

def make_gif_from_frames(png_paths, out_gif, duration=1000):
  """Crea un GIF a partir de una lista de rutas a PNGs."""
  frames = [imageio.imread(p) for p in png_paths]
  imageio.mimsave(out_gif, frames, duration=duration)
  return out_gif
