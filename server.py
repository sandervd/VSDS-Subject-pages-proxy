#!/usr/bin/env python
import rdflib
from flask import Flask, request
from flask_rdf.flask import returns_rdf
from flask_rdf.format import FormatSelector
from SPARQLWrapper import SPARQLWrapper, SPARQLWrapper2
import re

import subjectpages.renderer

app = Flask(__name__)

def endpoint_for_uri(uri):
    # @TODO Move this to config
    endpoints = {
        'http:\/\/example.org.*': 'http://example.org/sparql',
        # Default endpoint, set sparql endpoint here.
        '.*': 'http://vsds-demonstrator.ddev.site:7200/repositories/vsds'
    }
    for endpoint_regex in endpoints:
        if re.search(endpoint_regex, uri):
            return endpoints[endpoint_regex]
    raise Exception("No default endpoint set")

def endpoint_ontology_lookup():
    # @TODO Set ontology lookup endpoint and graph in config.
    return "http://vsds-demonstrator.ddev.site:7200/repositories/vsds"

@app.route('/')
@app.route('/<path:path>')
@returns_rdf
def subject_page(path=''):
    uri = request.args.get('uri')
    endpoint = endpoint_for_uri(uri)
    sparql = SPARQLWrapper(endpoint)
    sparql.setQuery("DESCRIBE <" + uri + ">")  # @TODO Insecure, SPARQL injection!
    graph = sparql.queryAndConvert()

    if FormatSelector().wants_rdf(accepts=request.headers.get('Accept')):
        return graph

    # @TODO limit query to only include predicates occuring in data.
    # Query could select for language of interface etc.
    sparql2 = SPARQLWrapper(endpoint_ontology_lookup())
    sparql2.setQuery("""
CONSTRUCT {?predicate <http://www.w3.org/2000/01/rdf-schema#label> ?label}
WHERE {
    GRAPH <http://ontologies/> {
        ?predicate <http://www.w3.org/2000/01/rdf-schema#label> ?label
    }                    
}
""")
    
    labels = sparql2.queryAndConvert()
    graph += labels
   
    return subjectpages.renderer.graph_to_html(rdflib.URIRef(uri), graph)


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
