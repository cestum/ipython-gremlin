
import ipycytoscape
import textwrap
import ipywidgets as widgets
from IPython.display import display

##Common graph styles
common_graph_style = [
    {
        'selector': 'node', 
        'css': {
            'background-color': 'green',
            'content': 'data(label)',
            'background-opacity': 0.333
        }
    },        
    {
        'selector': 'node[class="neighbour1"]',
        'style': {'background-opacity': 0.73, 'background-color': 'blue'}
    },
    {
        'selector': 'node[class="neighbour2"]',
        'style': {'background-opacity': 0.73, 'background-color': 'red'}
    },
    {
        "selector": "node.gleaf",
        "style": {"background-opacity": 0.73, "background-color": "#AAD8FF"}
    },    
    {
        'selector': 'node[class="all"]',
        'style': {'background-opacity': 0.73, 'background-color': 'purple'}
    },
    {'selector': 'edge', 'style': {
        'width': 4,
        'content': 'data(type)',
        'line-color': '#9dbaea',
        'target-arrow-shape': 'triangle',
        'target-arrow-color': '#9dbaea',
        'curve-style': 'bezier',
    }
    }
]

def highlight_leaf(cytograph):
    def callback(event):
        if event['name'] != 'value':
            return
        #add gleaf class for
        for node in cytograph.graph.nodes:
            if node.data["isleaf"]:
                classes = set(node.classes.split(" "))
                if event['new']:
                    classes.add("gleaf")
                else:
                    classes.remove("gleaf")
                node.classes = " ".join(classes)
    return callback


def set_layout(cytograph, options_widget):
    #used by breadfirst
    def show_directed(change):
        if change['name'] != 'value':
            return
        cytograph.set_layout(directed=change['new'])
    #show grid for breadthfirst
    #change node spacing
    def change_spacing(change):
        if change['name'] != 'value':
            return
        cytograph.set_layout(nodeSpacing=change['new'])

    #change edge length
    def change_edgelen(change):
        if change['name'] != 'value':
            return
        cytograph.set_layout(edgeLengthVal=change['new'])        

    #change spacing length
    def change_spacinglength(change):
        if change['name'] != 'value':
            return
        cytograph.set_layout(spacingFactor=change['new'])        
  

    def show_grid(change):
        if change['name'] != 'value':
            return
        cytograph.set_layout(grid=change['new'])        

    def show_gridlabels(change):
        if change['name'] != 'value':
            return
        cytograph.set_layout(nodeDimensionsIncludeLabels=change['new'])       
        
    def set_layout_options(layout):
        bottom_options_widgets=[]
        
        if layout == 'cola' or layout == 'cose':
            #node spacing length
            spacing_widget = widgets.IntSlider(
                value=210,
                description='Node Spacing'
            )
            spacing_widget.observe(change_spacing)
            bottom_options_widgets.append(spacing_widget)
            #edge length
            edge_spacing_widget = widgets.IntSlider(
                value=20,
                description='Edge length'
            )
            edge_spacing_widget.observe(change_edgelen)
            bottom_options_widgets.append(edge_spacing_widget)
        elif(layout == "breadthfirst"):
            #nodeDimensionsIncludeLabels=True,
            #avoidOverlap=True,
            #spacingFactor=0.6,
            #maximal=False,
            #grid=False,
            #nodeDimensionsIncludeLabels
#             nodeDimensionsIncludeLabels = widgets.Checkbox(
#                 value=True,
#                 description='Include Labels',
#                 disabled=False,
#                 indent=False
#             )
#             nodeDimensionsIncludeLabels.observe(show_gridlabels)
#             bottom_options_widgets.append(nodeDimensionsIncludeLabels)
            
            ##directed
            directed_widget = widgets.Checkbox(
                value=False,
                description='Directed',
                disabled=False,
                indent=False
            )
            directed_widget.observe(show_directed)
            bottom_options_widgets.append(directed_widget)
            ##Grid
            grid_widget = widgets.Checkbox(
                value=False,
                description='Grid',
                disabled=False,
                indent=False
            )
            grid_widget.observe(show_grid)
            bottom_options_widgets.append(grid_widget)            
            #spacing factor
            spacingFactor = widgets.FloatSlider(
                    value=0.6,
                    min=0.1,
                    max=5.0,
                    step=0.1,
                    description='Spacing Factor',
                    disabled=False,
                    readout_format='.1f'
            )
            spacingFactor.observe(change_spacinglength)
            bottom_options_widgets.append(spacingFactor)
            
        options_widget.children = bottom_options_widgets

    def callback(event):
        if event['name'] != 'value':
            return
        new_layout = event['new']
        set_layout_options(new_layout)
        cytograph.set_layout(name=new_layout)

    return callback




def draw_cytograph_graph(graph_data, style_data=common_graph_style, layout="cose", **kwargs):
    ipython_cytoscapeobj = ipycytoscape.CytoscapeWidget()
    ipython_cytoscapeobj.graph.add_graph_from_networkx(graph_data)
#     ipython_cytoscapeobj.set_tooltip_source('label')
    ipython_cytoscapeobj.set_style(style_data)

    ipython_cytoscapeobj.set_layout(name=layout, animate=False, **kwargs)    
    #show leaf button
    btn = widgets.ToggleButton(
        value=False,
        description="Highlight leaf", 
        disabled=False,
        button_style='success',
        icon='check'
    )
    btn.observe(highlight_leaf(ipython_cytoscapeobj))

    #show layout
    layout_choice_widget = widgets.Dropdown(
        options=['cola', 'concentric', 'grid', 'breadthfirst', 'cose', 'klay', 'dagre'], 
        description='Layout',
        value=layout
    )

    bottom_row = widgets.HBox([])
    layout_cb = set_layout(ipython_cytoscapeobj, bottom_row)
    layout_choice_widget.observe(layout_cb)
    top_row = widgets.HBox([btn, layout_choice_widget])
    #initializes layout
    layout_cb({
        "name":"value",
        "new":layout
    })
    
    return widgets.VBox([top_row, bottom_row]), ipython_cytoscapeobj