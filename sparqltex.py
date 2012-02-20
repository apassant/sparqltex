#!/usr/bin/env python

from SPARQLWrapper import SPARQLWrapper, JSON
import sys, os
import urllib
import simplejson

## Edit ad needed
PDFLATEX = '/usr/texbin/pdflatex'
## Do not edit (or change accordingly in sparql.sty)
TMPFILE = './tmpres'

def prefix(prefixes, query):
    ## Config file should go there
    prefixes = """
PREFIX bibtex: <http://zeitkunst.org/bibtex/0.1/bibtex.owl#>
PREFIX bio: <http://purl.org/vocab/bio/0.1/>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX swc: <http://data.semanticweb.org/ns/swc/ontology#>
PREFIX swcp: <http://apassant.net/home/2010/05/swcp/ns#>
PREFIX swrc: <http://swrc.ontoware.org/ontology#>
PREFIX vcard: <http://www.w3.org/2006/vcard/ns#>
PREFIX ical: <http://www.w3.org/2002/12/cal/icaltzd#>
PREFIX dc: <http://purl.org/dc/terms/>
"""
    return "%s %s" %(prefixes, query)

## Run the SPARQL query
def sparql(query, template, tlist, **kwargs):
    ## Get prefixes
    query = prefix('', input.query)
    ## Run through a SPARQL endpoint with curl
    if 'endpoint' in kwargs.keys():
        endpoint = kwargs['endpoint']
        url = "%s%s" %(endpoint, urllib.quote_plus(query))
        raw_json = urllib.urlopen(url).read()
    ## Run through a RDF file with roqet + any23 (helps to clean messy HTML)
    elif 'data' in kwargs.keys():
        data = kwargs['data']
        data = "'http://api.sindice.com/any23/any23/?format=best&uri=%s'" %urllib.quote_plus(data)
        cmd = 'roqet -e "%s" -D %s -r json 2>/dev/null' %(query, data)
        raw_json = os.popen(cmd).read()
    ## Get JSON in Python object and render
    json =  simplejson.loads(raw_json)
    return sparql_template(json, template, tlist)

## Transform JSON into LaTeX, using the template
def sparql_template(json, template, tlist):
    ## Get vars and data
    vars = json['head']['vars']
    res = json['results']['bindings']
    ## Render output
    l = ''
    s = ''
    if len(res) > 1:
        l = "\\begin{%s}\n" %tlist
        s = '\item '
    for r in res:
        foo = {}
        for v in vars:
            ## TODO - get a list of accentuated chars
            value = r[v]['value']
            value = value.replace('&eacute;', "\'{e}")
            value = value.replace('&', '\\&')
            value = value.replace('- ', '\item ')
            foo[str(v)] = value
        l += s + template % foo + '\n'
    if len(res) > 1:
        l += "\end{%s}\n" %tlist
    return l
    
## RUN
if __name__ == "__main__":
    argv = sys.argv
    if len(argv) == 1:
        print """
Usage: sparqltex foobar.tex
- foobar.tex : the TeX file to compile

See http://github.com/terraces/sparqltex for details
"""
    else:
        if argv[1] == '-run':
            input = __import__(argv[2])
            ## List type
            tlist = input.tlist if 'tlist' in dir(input) else 'itemize'
            ## Endpoint versus data
            if 'endpoint' in dir(input):
                l = sparql(input.query, input.template, tlist, endpoint = input.endpoint)
            elif 'data' in dir(input):
                l = sparql(input.query, input.template, tlist, data = input.data)
            file = open(TMPFILE, 'w')
            file.write(l.encode('utf-8'))
            file.close
        else:
            cmd = """%s -shell-escape %s""" %(PDFLATEX, argv[1])
            os.system(cmd)
