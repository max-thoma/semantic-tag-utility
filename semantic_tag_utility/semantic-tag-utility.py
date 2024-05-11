import argparse

import tools.ast_to_jsonld as ast_to_jsonld
import tools.ontology_to_tag as ontology_to_tag
import tools.sparql_queries as sparql_queries

# Path to the SysML v2 Metamodel
METADATA_DIR = "./res/jsonld/metamodel"

# Base uri for the RDF graph
BASE_URI = "http://tuwien.at/ns/"

DEFAULT_ONTOLOGY_NS = "https://www.w3.org/ns/sosa/"
DEFAULT_PREFIX_ONTOLOGY = "sosa:"
DEFAULT_PREFIX_LIB = "SOSA_"
DEFAULT_PACKAGE_NAME = "SosaTags"

DEFAULT_API_URL = "http://localhost:9000/"

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="semantic-tag-utility",
        description="Utility for generating and extracting semantic metadata tags for SysML v2 models",
        epilog="\033[1mThis software is as is and should not be used in production!\033[0;0m",
    )
    subparsers = parser.add_subparsers(dest="action")

    gen_library = subparsers.add_parser(
        "gen-library",
        help="Generate a semantic metadata tagging library for SysML v2 from an ontology",
    )
    gen_library.add_argument(
        "--input-ontology-ns",
        help=f"The ontology namespace for the generation of the SysML v2 tagging library e.g., '{DEFAULT_ONTOLOGY_NS}'",
        default=DEFAULT_ONTOLOGY_NS,
    )
    gen_library.add_argument(
        "-o", "--output", help="Path for the generated library file"
    )
    gen_library.add_argument(
        "-po",
        "--prefix-ontology",
        help="Prefix of the ontology, e.g., 'sosa:'",
        default=DEFAULT_PREFIX_ONTOLOGY,
    )
    gen_library.add_argument(
        "-pl",
        "--prefix-library",
        help="Prefix of the generated library, e.g., 'SOSA_'",
        default=DEFAULT_PREFIX_LIB,
    )
    gen_library.add_argument(
        "-n",
        "--package-name",
        help="Name of the generated SysML v2 package e.g., 'SosaTags'",
        default=DEFAULT_PACKAGE_NAME,
    )

    gen_jsonld = subparsers.add_parser(
        "gen-jsonld",
        help="Generates a JSON-LD file with the @context information from the SysML v2 metamodel from an SysML v2 AST serialized as JSON",
    )
    gen_jsonld.add_argument(
        "-i",
        "--input-ast-file",
        help="Path to the input JSON AST of the SysML v2 model",
    )
    gen_jsonld.add_argument(
        "-o", "--output-jsonld", help="Path to the output JSON-LD file"
    )
    gen_jsonld.add_argument(
        "-b", "--base-uri", help="Base URI used for output RDF graph", default=BASE_URI
    )
    gen_jsonld.add_argument(
        "-m",
        "--metadata-dir",
        help="Path to the SysML v2 metamodel JSON-LD files",
        default=METADATA_DIR,
    )

    transform_rdf = subparsers.add_parser(
        "transform-rdf",
        help="Transforms the SysML v2 RDF graph into the target ontology of the semantic metadata tags",
    )
    transform_rdf_group = transform_rdf.add_mutually_exclusive_group()
    transform_rdf_group.add_argument(
        "--api-endpoint",
        help="URL to the SysML API used to retrieve the elements of the most recent project",
        default=DEFAULT_API_URL,
    )
    transform_rdf_group.add_argument(
        "-i",
        "--input-model",
        help="Path to the RDF representation of SysML model in JSON-LD",
    )
    transform_rdf.add_argument(
        "-o", "--output-rdf", help="Path to the transformed serialized RDF graph"
    )
    transform_rdf.add_argument(
        "-b", "--base-uri", help="Base URI used for output RDF graph", default=BASE_URI
    )

    transform_rdf.add_argument(
        "--input-ontology-ns",
        help=f"The ontology namespace used by the tagging library e.g., '{DEFAULT_ONTOLOGY_NS}'",
        default=DEFAULT_ONTOLOGY_NS,
    )
    transform_rdf.add_argument(
        "-po",
        "--prefix-ontology",
        help="Prefix of the ontology, e.g., 'sosa:'",
        default=DEFAULT_PREFIX_ONTOLOGY,
    )
    transform_rdf.add_argument(
        "-pl",
        "--prefix-library",
        help="Prefix of the generated library, e.g., 'SOSA_'",
        default=DEFAULT_PREFIX_LIB,
    )
    args = parser.parse_args()

    match args.action:
        case "gen-library":
            print(f"Generating tagging library for '{args.input_ontology_ns}'")
            ontology_to_tag.ontology_to_tag(
                args.input_ontology_ns,
                args.prefix_ontology,
                args.prefix_library,
                args.output,
                args.package_name,
            )
            exit(0)
        case "gen-jsonld":
            print(
                f"Generating JSON-LD file for '{args.input_ast_file}', using '@context' information from '{args.metadata_dir}'"
            )
            ast_to_jsonld.ast_to_jsonld(
                args.input_ast_file,
                args.output_jsonld,
                args.base_uri,
                args.metadata_dir,
            )
            exit(0)
        case "transform-rdf":
            print("Retrieving semantic tags and transforming RDF graph")
            sparql_queries.transform_rdf(
                args.api_endpoint,
                args.input_model,
                args.output_rdf,
                args.base_uri,
                args.input_ontology_ns,
                args.prefix_ontology,
                args.prefix_library,
            )
            exit(0)
        case default:
            parser.print_help()
