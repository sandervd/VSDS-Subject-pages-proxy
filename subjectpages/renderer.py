from jinja2 import Environment, PackageLoader, select_autoescape
from rdflib.term import Literal



env = Environment(
    loader=PackageLoader("subjectpages"),
    autoescape=select_autoescape(),
    extensions=['jinja2.ext.debug']
)

def graph_to_html(uri, graph):
    template = env.get_template("triples.html.jinja")
    html = template.render(graph=graph, subject_uri=uri)
    return html

def _is_literal(node):
    if isinstance(node, Literal):
        return True
    return False

def _has_contents(node):
    if (len(list(node)) == 0):
        return False
    return True

env.tests["literal"] = _is_literal
env.tests["has_contents"] = _has_contents