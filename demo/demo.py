from pyKanka.Grapher import Grapher
from pyKanka.KankaHandler import KankaHandler
from igraph import plot

H = KankaHandler()
H.set_endpoints(['characters', 'families', 'organisations', 'creatures', 'events', 'items', 'locations', 'notes'])

H.kanka_sync()

G = Grapher(H.generate_adjecency_list())
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

