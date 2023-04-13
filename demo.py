from igraph import Graph as g
from igraph import plot
import igraph as ig

def demo():
    import KankaHandler

    H = KankaHandler.KankaHandler()
#    H.endpoints = ['characters', 'events', 'items', 'locations', 'notes',
#                   'organisations']
    H.kanka_sync()

    G = Grapher(H.generate_adjecency_list())
    components = G.graph.connected_components(mode='strong')
    def colf(l):
        r = ''
        for i in l:
            r += i + '\n'
        return r
    comp = G.print_connected_comp().cluster_graph(combine_vertices={'name':colf})
    layout, e_comp = g.layout_sugiyama(comp, maxiter=500,
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



class Grapher:
    def __init__(self, adjacency_list):
        self.graph =  g.ListDict(adjacency_list, directed = True)

        layout = self.graph.layout_davidson_harel(maxiter=100, fineiter=10,
                                                   weight_edge_crossings=2)
        self.graph.vs['x'] = [x for x,y in layout.coords]
        self.graph.vs['y'] = [y for x,y in layout.coords]

        self.vis = {
            'layout' : 'auto',
            'bbox' : (2000, 2000),
            'target' : 'graph.svg',
            'vertex_label' : self.graph.vs['name'],
            'vertex_shape' : 'rectangle',
            'autocurve' : False,
        }
        self.view = self.graph

    def local(self, name, dist, mode='all'):
        local =[]
        for i, d, p in self.graph.bfsiter(self.graph.vs['name'].index(name),
                                          mode=mode , advanced=True):
            if d > dist:
                break
            local += [i]
        self.view = self.graph.induced_subgraph(local)

    def show(self):
        #self.vis['layout'] = self.graph.layout_davidson_harel(maxiter=100, fineiter=10,
        #                                           weight_edge_crossings=2)
        self.vis['vertex_label'] = self.view.vs['name']
        plot(self.view, **self.vis)

    def write(self, target):
        self.vis['target'] = target
        self.show()

    def reset(self):
        self.view = self.graph

    def print_connected_comp(self):
        '''
        generates the connected components for the graph
        '''
        for e in self.graph.es:
            s = e.source
            t = e.target
            e['weight'] =  float(self.graph.degree(s)) +  float(self.graph.degree(t))

        components = self.graph.connected_components(mode='strong')
        layout = components.graph.layout_davidson_harel(
            maxiter = 200,
            fineiter = 10,
            cool_fact = 0.95,
            weight_node_dist = 1,
            weight_edge_lengths = -1,
            weight_edge_crossings = -1,
            weight_node_edge_dist = -1
        )
        print(components.graph.density())
        plot(
            components,
            bbox = (4000, 4000),
            layout = layout,
            target='con_comp.svg',
            vertex_size=10,
            palette=ig.RainbowPalette(),
            edge_width=0.7,
            autocurve = False,
            vertex_shape = 'rectangle',
            vertex_label = components.graph.vs['name']
        )
        
        return components



