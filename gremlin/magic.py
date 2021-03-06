"""IPython Gremlin custom magic"""
import atexit
import ssl

from traitlets import Unicode, Dict, Float, Bool, Instance
from IPython.core.error import TryNext
from IPython.core.magic import (Magics, magics_class, line_magic, cell_magic,
                                line_cell_magic, needs_local_scope)


from gremlin import config, registry, utils
from gremlin.cytoscape import draw_cytograph_graph

@magics_class
class GremlinMagic(Magics):
    """
    First of all, keep him out of the light, he hates bright light, especially
    sunlight, it'll kill him. Second, don't give him any water, not even to
    drink. But the most important rule, the rule you can never forget, no
    matter how much he cries, no matter how much he begs, never feed him after
    midnight.
    """

    aliases = Dict(
        config.defaults.aliases, allow_none=True, config=True, help="""
        Aliases for underlying graph
    """)

    password = Unicode(config.defaults.password, config=True, help="""
        Password used in SASL authentication
    """)

    response_timeout = Float(
        config.defaults.response_timeout,
        allow_none=True, config=True, help="""
        Timeout for server response
    """)

    ssl_context = Instance(
        klass=ssl.SSLContext, default_value=config.defaults.ssl_context,
        allow_none=True, config=True, help="""
        `ssl.SSLContext` object for SSL
    """)

    uri = Unicode(config.defaults.uri, config=True, help="""
        Default database URI if none is defined inline
    """)

    username = Unicode(config.defaults.username, config=True, help="""
        Username used in SASL authentication
    """)

    @needs_local_scope
    @line_cell_magic('gremlin')
    def gremlin(self, line, cell=None, local_ns={}):
        """I make the illogical logical"""
        if cell is None:
            connection_str = ''
            script = line.lstrip("\n")
        else:
            connection_str = line
            script = cell
        user_ns = self.shell.user_ns
        # print(user_ns.keys())
        bindings_key = {}
            
        for k,v in user_ns.items():
            if not k.startswith("_"):
                bindings_key[k] = v

        # bindings_key.update(local_ns)        
        descriptors = utils.parse(connection_str)
        connection = registry.ConnectionRegistry.get(descriptors, self)
        return utils.submit(script, bindings_key, self.aliases, connection)

    # @cell_magic('gremlin.cytoscape')
    # def to_cytoscape(self, line, cell=None, local_ns={}):  
    #     """
    #     Generates cytoscape widge based on ipycytoscape. 
    #     """
    #     print(line)
    #     if len(line) > 0:
    #         lines = line.split(" ")
    #         linesmap = dict(l.split("=") for l in lines if '=' in l)
    #         print(linesmap)
        
    #     options={}
    #     user_ns = self.shell.user_ns
    #     for k,v in linesmap.items():
    #         options[k] = user_ns.get(k,v)

    #     print(user_ns.get(""))
    #     first_results = self.gremlin(options.get('connection',''), cell=cell, local_ns=local_ns)
    #     return first_results.to_cytoscape()

    @line_magic('gremlin.close')
    def close(self, line):
        """Explicity close underlying DB connections"""
        registry.ConnectionRegistry.close()

    @line_magic('gremlin.connection.close')
    def close_connection(self, line):
        registry.ConnectionRegistry.close(line)

    @line_magic('gremlin.connection.set_alias')
    def set_connection_alias(self, line):
        """Set alias for specified connection"""
        descriptors = utils.parse(line)
        registry.ConnectionRegistry.set_connection_alias(descriptors, self)

    @line_magic('gremlin.connection.set_current')
    def set_current_connection(self, line):
        """Set specified connection as current"""
        descriptors = utils.parse(line)
        registry.ConnectionRegistry.set_current_connection(descriptors, self)

    @line_magic('gremlin.connection.current')
    def get_current_connection(self, line):
        """Get the currently used connection object"""
        return registry.ConnectionRegistry.current

    @line_magic('gremlin.draw_graph')
    def drawgraph(self, line):
        print(line)

def close():
    """uh oh"""
    print('CLOSING GREMLIN SERVER CONNECTIONS')
    registry.ConnectionRegistry.close()


atexit.register(close)


def load_ipython_extension(ip):
    """Load the extension in IPython."""
    ip.register_magics(GremlinMagic)
