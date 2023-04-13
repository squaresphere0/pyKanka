import Grapher
import KankaHandler
from igraph import plot

H = KankaHandler.KankaHandler()
#    H.endpoints = ['characters', 'events', 'items', 'locations', 'notes',
#                   'organisations']
H.kanka_sync()

G = Grapher.Grapher(H.generate_adjecency_list())
components = G.graph.connected_components(mode='strong')

# List of entries in a connected component
def colf(l):
    r = ''
    for i in l:
        r += i + '\n'
    return r
comp = G.print_connected_comp().cluster_graph(combine_vertices={'name':colf})
layout, e_comp = comp.layout_sugiyama( maxiter=500,
                                   return_extended_graph=True)

layout.rotate(-1)
plot(
    comp,
    bbox = (5000, 5000),
    margin = 100,
    layout = layout,
    #autocurve=False,
    vertex_shape = 'circle',
    target = 'contracted.svg',
    vertex_label = comp.vs['name']
)

