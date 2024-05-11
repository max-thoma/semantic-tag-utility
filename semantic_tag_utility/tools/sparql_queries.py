import rdflib
import tools.api_client as api_client


def transform_rdf(
    api_endpoint,
    input_model,
    output_rdf,
    base_uri,
    input_ontology,
    prefix_ontology,
    prefix_library,
):
    g = rdflib.Graph(base=base_uri)

    if input_model is not None:
        g.parse(input_model, format="json-ld")
        g.bind("sysml", "http://omg.org/ns/sysml/v2/metamodel#")
        g.bind("base", base_uri)
    else:
        elements, base_uri = api_client.download_latest_elements(api_endpoint)
        g.parse(elements, format="json-ld")
        g = rdflib.Graph(base=base_uri)

    print(f"Model Graph has {len(g)} statements.")
    g.serialize(format="turtle", destination="out.ttl")
    sosa_g = _construct_sosa(
        g, base_uri, input_ontology, prefix_ontology, prefix_library
    )
    sosa_g.serialize(format="turtle", destination=output_rdf)


def _construct_sosa(g, base, input_ontology, prefix_ontology, prefix_library):
    g1 = _extract_metadata_tags(
        g, base, input_ontology, prefix_ontology, prefix_library
    )
    g2 = _extract_connection_tags(
        g, base, input_ontology, prefix_ontology, prefix_library
    )
    g_sosa = g1 + g2
    print(g_sosa.serialize(format="turtle"))
    return g_sosa


def _extract_metadata_tags(g, base, input_ontology, prefix_ontology, prefix_library):
    query = f"""
    PREFIX sysml: <http://omg.org/ns/sysml/v2/metamodel#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    CONSTRUCT {{ ?element rdf:type ?s; rdf:label ?element_name_short; rdf:comment ?element_name_long }}
    WHERE {{
        ?metadata_usg a sysml:MetadataUsage .
        ?metadata_usg sysml:itemDefinition ?def .
        ?def sysml:declaredName ?uri_string .
        ?metadata_usg sysml:annotatedElement ?element .
        OPTIONAL {{
            ?element sysml:declaredName ?element_name_short .
            ?element sysml:qualifiedName ?element_name_long .
        }}

        BIND((REPLACE(?uri_string, "^{prefix_library}", "{input_ontology}")) AS ?full_uri) .
        BIND((URI(?full_uri)) AS ?s) .
    }}
    """

    qres = g.query(query)
    s = qres.serialize(format="turtle")
    new_g = rdflib.Graph()
    new_g.parse(s)
    if prefix_ontology.endswith(":"):
        prefix_ontology = prefix_ontology[0:-1]
    new_g.bind(prefix_ontology, input_ontology)
    new_g.bind("rdf", "http://www.w3.org/1999/02/22-rdf-syntax-ns#")
    new_g.bind("base", base)

    return new_g


def _extract_metadata_tags_ownership(g, base, input_ontology, prefix_ontology, prefix_library):
    query = f"""
    PREFIX sysml: <http://omg.org/ns/sysml/v2/metamodel#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    CONSTRUCT {{ ?element rdf:type ?s; rdf:label ?element_name_short; rdf:comment ?element_name_long }}
    WHERE {{
        ?metadata_usg a sysml:MetadataUsage .
        ?metadata_usg sysml:ownedRelationship ?owned .
        ?owned sysml:type ?def .
        ?def sysml:declaredName ?uri_string .
        ?metadata_usg sysml:owningRelationship ?owning .
        ?owning sysml:source ?element .
        ?element sysml:declaredName ?element_name_short .

        OPTIONAL {{
            ?element sysml:qualifiedName ?element_name_long .
        }}

        BIND((REPLACE(?uri_string, "^{prefix_library}", "{input_ontology}")) AS ?full_uri) .
        BIND((URI(?full_uri)) AS ?s) .
    }}
    """

    qres = g.query(query)
    s = qres.serialize(format="turtle")
    new_g = rdflib.Graph()
    new_g.parse(s)
    if prefix_ontology.endswith(":"):
        prefix_ontology = prefix_ontology[0:-1]
    new_g.bind(prefix_ontology, input_ontology)
    new_g.bind("rdf", "http://www.w3.org/1999/02/22-rdf-syntax-ns#")
    new_g.bind("base", base)

    return new_g


def _extract_connection_tags(g, base, input_ontology, prefix_ontology, prefix_library):
    query = f"""
    PREFIX sysml: <http://omg.org/ns/sysml/v2/metamodel#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    CONSTRUCT {{ ?source_element ?p ?target_element }}
    WHERE {{
         {{
            SELECT ?source_element ?target_element ?uri_string
            WHERE {{
                ?sub_connection a sysml:ConnectionUsage .
                ?sub_connection sysml:declaredName ?uri_string .
                ?sub_connection sysml:source ?source_element .
                ?sub_connection sysml:target ?target_element .
                ?target_element a sysml:PartUsage .
                ?source_element a sysml:PartUsage .
            }}
        }}
        UNION
        {{
            SELECT ?source_element ?target_element ?uri_string
            WHERE {{
                ?sub_connection a sysml:ConnectionUsage .
                ?sub_connection sysml:declaredName ?uri_string .
                ?sub_connection sysml:source ?source_element .
                ?sub_connection sysml:target ?target_feature .
                ?target_feature a sysml:Feature .
                ?source_element a sysml:PartUsage .
                ?feature_chain_tar a sysml:FeatureChaining .
                ?feature_chain_tar sysml:featureChained ?target_feature .
                ?feature_chain_tar sysml:target ?target_element .
            }}
        }}
        UNION
        {{
            SELECT ?source_element ?target_element ?uri_string
            WHERE {{
                ?sub_connection a sysml:ConnectionUsage .
                ?sub_connection sysml:declaredName ?uri_string .
                ?sub_connection sysml:source ?source_feature .
                ?sub_connection sysml:target ?target_element .
                ?target_element a sysml:PartUsage .
                ?source_feature a sysml:Feature .
                ?feature_chain_src a sysml:FeatureChaining .
                ?feature_chain_src sysml:featureChained ?source_feature .
                ?feature_chain_src sysml:target ?source_element .
            }}
        }}
        UNION
        {{
            SELECT ?source_element ?target_element ?uri_string
            WHERE {{
                ?sub_connection a sysml:ConnectionUsage .
                ?sub_connection sysml:declaredName ?uri_string .
                ?sub_connection sysml:source ?source_feature .
                ?sub_connection sysml:target ?target_feature .
                ?target_feature a sysml:Feature .
                ?source_feature a sysml:Feature .
                ?feature_chain_tar a sysml:FeatureChaining .
                ?feature_chain_src a sysml:FeatureChaining .
                ?feature_chain_tar sysml:featureChained ?target_feature .
                ?feature_chain_src sysml:featureChained ?source_feature .
                ?feature_chain_scr sysml:target ?source_element .
                ?feature_chain_tar sysml:target ?target_element .
            }}
        }}
        BIND((REPLACE(?uri_string, "^{prefix_library}", "{input_ontology}")) AS ?full_uri) .
        BIND((URI(?full_uri)) AS ?p) .
    }}
    """

    qres = g.query(query)
    s = qres.serialize(format="turtle")
    new_g = rdflib.Graph()
    new_g.parse(s)
    new_g.bind("rdf", "http://www.w3.org/1999/02/22-rdf-syntax-ns#")
    if prefix_ontology.endswith(":"):
        prefix_ontology = prefix_ontology[0:-1]
    new_g.bind("base", base)

    return new_g
