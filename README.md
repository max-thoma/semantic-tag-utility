# Semantic Tag Utility

The `semantic-tag-utility` provides tooling for generating and extracting semantic metadata tags for SysML v2 models.
It has three main feature:

1. Generation of SysML v2 tagging library based on a semantic web ontology
2. Enriching the SysML v2 AST with `@context` information from the SysML v2 Metamodel
3. Extracting and transforming of the SysML v2 model's RDF graph

## Installation

The semantic-tag-utility is writen in Python. It uses [rdflib](https://rdflib.readthedocs.io/en/stable/) for all RDF related tasks and [requests](https://requests.readthedocs.io/en/latest/) for the optional SysML v2 API Services integration.
The project is managed using [poetry](https://python-poetry.org).
For creating SysML v2 models and generating their ASTs, it is recommended to use the current [release](https://github.com/Systems-Modeling/SysML-v2-Release) of the SysML v2 language. If you want to follow the [Tutorial](<README.md#Step-by-Step Tutorial>) you should install the SysML v2 JupyterLab environment.

To install the projects dependencies it is recommended to use [poetry](https://python-poetry.org).

```sh
  poetry install
```

In order to transform a SysML v2 model's AST to an RDF graph, the semantic-tag-utility needs access to the SysML v2 Metamodel JSON-LD files.
They are located in the [SysML v2 API Services repository](https://github.com/Systems-Modeling/SysML-v2-API-Services/tree/master/public/jsonld/metamodel). 
If you want to download them, you can clone their repository with

```sh
git clone https://github.com/Systems-Modeling/SysML-v2-API-Services.git
```

The metamodel JSON-LD files are then located at `SysML-v2-API-Services/public/jsonld/metamodel`

Alternatively, you can download their latest release and unzip it
```sh
wget https://github.com/Systems-Modeling/SysML-v2-API-Services/archive/refs/tags/2024-02.zip
unzip 2024-02.zip
```

The metamodel JSON-LD files are then located at `SysML-v2-API-Services-2024-02/public/jsonld/metamodel`

## Usage

To run the project it is recommended to use [poetry](https://python-poetry.org).

```sh
  poetry run semantic-tag-utility.py --help
```

This will print out detailed usage information.
To get detailed information about the individual commands, you can use

```sh
  poetry run semantic-tag-utility.py gen-library --help
  poetry run semantic-tag-utility.py gen-jsonld --help
  poetry run semantic-tag-utility.py transform-rdf --help
```

## Step-by-Step Tutorial

Prerequisites:
- [Installed](README.md#Installation) semantic-tag-tool
- Installed [SysML v2 tool chain](https://github.com/Systems-Modeling/SysML-v2-Release) with the JupyterLab environment working.
- For the conversion form the model's AST to RDF either:
  - [Downloaded](README.md#Installation) SysML v2 Metamodel JSON-LD files (recommended)
  - Installed [SysML v2 API Services](https://github.com/Systems-Modeling/SysML-v2-API-Services/tree/master) running locally

Let's start with a simple SysML v2 model. That has a part definition and part usage.

```sysml
package Tutorial {
    part def TutorialSystem;
    part TutorialSensor: TutorialSystem;
}
```
The model represents a system that has one _sensor_.
However, currently it does not contain any semantic information about the sensor.
We only know that `TutorialSensor` is supposed to be as sensor, because of its declared name.
If we want to express that `TutorialSensor` is sensor as it is defined in the [SOSA](https://www.w3.org/TR/vocab-ssn/) ontology, we can do this with the help of the semantic-tag-utility.
First, we have to generate a tagging library based on SOSA.
To do this we simply call

```sh
poetry run python semantic-tag-utility.py gen-library \
         --input-ontology-ns "http://www.w3.org/ns/sosa/" \
         --prefix-ontology "sosa" \
         --prefix-library "SOSA_" \
         --package-name "SOSA" \
         --output "SOSA_Tags.sysml"
```
        
This will generate a file called `SOSA_Tags.sysml` that contains all the metadata and connection definitions needed for tagging the model.
Every `rdfs:Class` and `owl:Class` from the SOSA ontology was converted to metadata definition.
The contents will look something like this:

```sysml
package SosaTags {
	//  This package was auto-generated

	//  https://www.w3.org/ns/sosa/Sensor
	metadata def SOSA_Sensor;

}
```

Next, we import the generated library as package into the model. 
Then, the `TutorialSensor` can be tagged with `SOSA_Sensor`.

```sysml
package Tutorial {
    import SOSA::*;

    part def TutorialSystem;
    part TutorialSensor: TutorialSystem {@SOSA_Sensor{}}
}
```

To generate the AST of the model we can use the `%export Tutorial` command in the SysML v2 JupyterLab environment.
To display the package structure we can use `%show Tutorial`, and for visualization of the `Tutorial` package we can call `%viz Tutorial`.

We call

```
%export Tutorial
```
to generate the downloadable AST JSON file of the model.

In the next step, the AST of the model is enriched with `@context` information from the SysML v2 Metamodel.
This is done in order to generate a proper RDF graph.
To do so, we use the following command from the semantic-tag-utility:

```sh
poetry run python semantic-tag-utility.py gen-jsonld \
  --input-ast-file Tutorial.json \
  --output-jsonld Tutorial.jsonld \
  --base-uri "http://example.com/" \
  --metadata-dir "path/to/SysML/v2/metamodel"
```

Notice that we have to supply the path SysML v2 metamodel JSON-LD files. 
They are _not packaged_ with this utility. 
They are located in [this](https://github.com/Systems-Modeling/SysML-v2-API-Services/tree/master/public/jsonld/metamodel) repository.
In the [Installation](README.md#Installation) section of the README.md, you can find instructions how to download them.

The last step is to extract the semantic metadata information from the model's RDF graph.
To do so, we use this command:

```sh
 poetry run python semantic-tag-utility.py transform-rdf \
  --input-model Tutorial.jsonld \
  --output-rdf Tutorial.ttl \
  --base-uri "http://example.com/" \
  --input-ontology-ns "http://www.w3.org/ns/sosa/" \
  --prefix-ontology "sosa:" \
  --prefix-library "SOSA_"
```

This will produce the following output:

```turtle
@prefix base: <http://example.com/> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix sosa: <http://www.w3.org/ns/sosa/> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

base:3e917745-f059-4098-8183-ee7ed1629a09 a sosa:Sensor ;
    rdf:comment "Tutorial::TutorialSensor"^^xsd:string ;
    rdf:label "TutorialSensor"^^xsd:string .
```

The `TutorialSensor` part was transformed to be `sosa:Sensor` type preserving its original element URI.
Its original `qualified` name is used as comment, and it has its `declared` name as a label.

### Summary

We have done the following steps:

- Created a SysML v2 Model
- Generated a semantic tagging library based on the SOSA ontology
- Tagged the model
- Generated the AST of the model
- Enriched the AST with the SysML v2 Metamodel
- Transformed the model's RDF graph into the target ontology (SOSA).

### Next Steps

The transformed RDF graph can now be used as run-time model of our model. We can update or transform it to our likings or use it with other tools. What is more, instead of manually calling the CLI tool, the CI/CD integration can be used to automate the aforementioned steps.

## CI/CD Integration

This repository contains a sample CI/CD integration, that performs all transformation steps automatically. Simply update the SysML model in the `model` directory and push the changes. The GitHub workflow will be executed and the transformed graph is returned as an artifact. To configure the workflow, change the values in the `.env` file in the `model` directory.

## Implementation Details

If you want to take a closer look at the implementation of the semantic-tag-utility you can check out these files:

- `semantic_tag_utility.py`: this is the CLI wrapper for the other tools
- `tools/ast_to_jsonld.py`: conversion form the AST to a proper RDF graph
- `tools/ontology_to_tag.py`: generation of the SysML v2 tagging library:
  1. Parses the input ontology
  2. Searches for all _subjects_ that are of type `rdfs:Class` or `owl:Class` and converts them to SysML v2 metadata definitions
  3. Searches for all _subjects_ that are of type `owl:ObjectProperty` and converts them to SysML v2 connection definitions
  4. Creates a package with the metadata and connection definitions
- `tools/sparql_queries.py`: performs the RDF graph transformation:
  1. Parses the RDF graph
  2. Extracts all the metadata information
  3. Extracts all connection information
  4. Combines them into a new RDF graph
- `tools/api_client.py`: this is a tool that downloads all elements in JSON-LD format of the latest project from the SysML v2 API services.
  
### Extraction of Metadata Tags

The semantic-tag-utility uses the RDF node structure displayed in the diagram below

![MetadataUsage node structure](./diagrams/metadata.svg)

Every usage of a metadata tag in the SysML v2 model create a `MetadataUsage`.
This node links to its `MetadataDefinition` and the `annotatedElement`, e.g., a `PartUsage`.
The `declaredName` in the `MetadataDefinition` then gets converted to a proper URI by the SPARQL query.

### Extraction of Connection Tags

The extraction of the connection information is a bit more involved.

![ConnectionUsage node structure](./diagrams/connection.svg)

If an element that is not a `PartUsage` is used in a connection, a new `Feature` node will be introduced.
Together with the `FeatureChaining` node, this can than be tracked back the actual element e.g., an `AttributeUsage`.
Likewise, the `declaredName` of the `ConnectionUsage` is converted to a proper URI by the SPARQL query.


## Contact

If you run into any problems, or you want to collaborate please open an issue.

## Third Party Libraries

This project uses the following Third Party Libraries:

- [rdflib](https://github.com/RDFLib/rdflib), licensed under [BSD-3-Clause](https://github.com/RDFLib/rdflib/blob/main/LICENSE).
- [requests](https://github.com/psf/requests), licensed under [Apache-2.0](https://github.com/psf/requests/blob/main/LICENSE).

For the CI/CD Integration:

- The Metamodel form the [SysML v2 API and Services](https://github.com/Systems-Modeling/SysML-v2-API-Services), licensed under [LGPL](https://github.com/Systems-Modeling/SysML-v2-API-Services/blob/master/LICENSE).
- The Jupyter Kernel from the [SysML v2 Pilot Implementation Protoyping](https://github.com/Systems-Modeling/SysML-v2-Pilot-Implementation), licensed under [LGPL](https://github.com/Systems-Modeling/SysML-v2-Pilot-Implementation/blob/master/LICENSE).