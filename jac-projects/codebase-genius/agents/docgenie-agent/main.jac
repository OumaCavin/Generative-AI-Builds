# DocGenie Agent - Automatic Code Documentation Generator
# Phase 5 Implementation: Generate comprehensive documentation from CCG data

import py from json;
import py from datetime;
import py from pathlib;
import py from re;
import py from typing;
import py from collections;
import py from jinja2;
import py from graphviz import Digraph;
import py from plantuml;

node DocGenieConfig {
    has template_dir: str = "./templates";
    has output_dir: str = "./outputs";
    has diagram_enabled: bool = true;
    has diagram_format: str = "png";  # png, svg, pdf
    has citation_style: str = "github";  # github, apa, ieee
    has doc_structure: str = "comprehensive";  # comprehensive, summary, detailed
}

node CodeEntity {
    has entity_id: str;
    has name: str;
    has type: str;  # function, class, method, module, variable
    has file_path: str;
    has start_line: int;
    has end_line: int;
    has complexity: float = 0.0;
    has dependencies: list = [];
    has dependents: list = [];
    has documentation: str = "";
    has source_code: str = "";
}

node Relationship {
    has from_entity: str;
    has to_entity: str;
    has relationship_type: str;  # calls, imports, inherits, contains, uses
    has confidence: float = 0.0;
    has context: str = "";
}

node DocumentationSection {
    has section_id: str;
    has title: str;
    has content: str;
    has order: int;
    has section_type: str;  # overview, api, architecture, examples
    has related_entities: list = [];
}

node GeneratedDocument {
    has title: str;
    has sections: list = [];
    has diagrams: list = [];
    has citations: dict = {};
    has metadata: dict = {};
}

walker generate_documentation {
    has ccg_data: dict = {};
    has repository_info: dict = {};
    has config: DocGenieConfig = DocGenieConfig();
    has generated_doc: GeneratedDocument = GeneratedDocument();
    
    can initialize_config with `root entry {
        print("[DocGenie] Initializing documentation generation configuration...");
        
        # Load configuration from config/config.json if exists
        config_path = "./config/config.json";
        if (pathlib.Path(config_path).exists()) {
            with open(config_path) as f:
                user_config = json.load(f);
            
            config.template_dir = user_config.get("template_dir", config.template_dir);
            config.output_dir = user_config.get("output_dir", config.output_dir);
            config.diagram_enabled = user_config.get("diagram_enabled", config.diagram_enabled);
            config.diagram_format = user_config.get("diagram_format", config.diagram_format);
            config.citation_style = user_config.get("citation_style", config.citation_style);
            config.doc_structure = user_config.get("doc_structure", config.doc_structure);
        }
        
        print(f"[DocGenie] Configuration loaded: {config}");
    }
    
    can validate_ccg_data with `root entry {
        print("[DocGenie] Validating CCG data structure...");
        
        if (not ccg_data) {
            raise ValueError("No CCG data provided for documentation generation");
        }
        
        required_keys = ["entities", "relationships", "metadata"];
        for key in required_keys {
            if (key not in ccg_data) {
                raise ValueError(f"CCG data missing required key: {key}");
            }
        }
        
        print(f"[DocGenie] CCG data validated: {len(ccg_data.get('entities', []))} entities, {len(ccg_data.get('relationships', []))} relationships");
    }
    
    can analyze_code_entities with `root entry {
        print("[DocGenie] Analyzing code entities for documentation...");
        
        entities_data = ccg_data.get("entities", []);
        
        # Convert entities to CodeEntity nodes
        entities_map = {};
        for entity_data in entities_data {
            entity = CodeEntity(
                entity_id=entity_data.get("id", ""),
                name=entity_data.get("name", ""),
                type=entity_data.get("type", ""),
                file_path=entity_data.get("file_path", ""),
                start_line=entity_data.get("start_line", 0),
                end_line=entity_data.get("end_line", 0),
                complexity=entity_data.get("complexity", 0.0),
                dependencies=entity_data.get("dependencies", []),
                dependents=entity_data.get("dependents", []),
                documentation=entity_data.get("documentation", ""),
                source_code=entity_data.get("source_code", "")
            );
            entities_map[entity.entity_id] = entity;
        }
        
        print(f"[DocGenie] Processed {len(entities_map)} code entities");
        report entities_map=entities_map;
    }
    
    can analyze_relationships with `root entry {
        print("[DocGenie] Analyzing entity relationships...");
        
        relationships_data = ccg_data.get("relationships", []);
        
        # Convert relationships to Relationship nodes
        relationships = [];
        for rel_data in relationships_data {
            relationship = Relationship(
                from_entity=rel_data.get("from", ""),
                to_entity=rel_data.get("to", ""),
                relationship_type=rel_data.get("type", ""),
                confidence=rel_data.get("confidence", 0.0),
                context=rel_data.get("context", "")
            );
            relationships.append(relationship);
        }
        
        print(f"[DocGenie] Processed {len(relationships)} relationships");
        report relationships=relationships;
    }
    
    can create_documentation_templates with `root entry {
        print("[DocGenie] Creating documentation templates...");
        
        templates = {
            "overview": """# {{ repository_name }} - Codebase Analysis

## Overview
{{ overview_description }}

**Repository**: {{ repository_url }}
**Generated**: {{ generation_date }}
**Analyzer**: {{ analyzer_version }}

## Quick Statistics
- **Total Files**: {{ total_files }}
- **Total Entities**: {{ total_entities }}
- **Total Relationships**: {{ total_relationships }}
- **Average Complexity**: {{ avg_complexity }}

## Architecture Overview
{{ architecture_summary }}

## High-Level Structure
{{ structure_summary }}
""",
            
            "api_reference": """# API Reference

## Classes
{% for class in classes %}
### {{ class.name }}
**File**: `{{ class.file_path }}` (lines {{ class.start_line }}-{{ class.end_line }})
**Complexity**: {{ class.complexity }}

{{ class.documentation if class.documentation else "No documentation available." }}

#### Methods
{% for method in class.methods %}
- **{{ method.name }}** ({{ method.type }}) - Complexity: {{ method.complexity }}
{% endfor %}

#### Dependencies
{% for dep in class.dependencies %}
- {{ dep }}
{% endfor %}

---
{% endfor %}

## Functions
{% for func in functions %}
### {{ func.name }}
**File**: `{{ func.file_path }}` (lines {{ func.start_line }}-{{ func.end_line }})
**Complexity**: {{ func.complexity }}

{{ func.documentation if func.documentation else "No documentation available." }}

#### Parameters
{% if func.parameters %}
{% for param in func.parameters %}
- **{{ param.name }}** ({{ param.type }}) - {{ param.description }}
{% endfor %}
{% else %}
- No parameters documented
{% endif %}

#### Dependencies
{% for dep in func.dependencies %}
- {{ dep }}
{% endfor %}

---
{% endfor %}
""",
            
            "architecture": """# Architecture Analysis

## System Components
{{ components_summary }}

## Dependency Graph
{{ dependency_analysis }}

## Complexity Analysis
{{ complexity_summary }}

## Design Patterns Detected
{{ patterns_summary }}
""",
            
            "examples": """# Usage Examples

## Function Usage
{% for func in functions %}
### {{ func.name }}
```{{ func.language or 'python' }}
{{ func.example_code }}
```

**Context**: {{ func.example_context }}
{% endfor %}

## Class Usage
{% for class in classes %}
### {{ class.name }}
```{{ class.language or 'python' }}
{{ class.usage_example }}
```

**Context**: {{ class.usage_context }}
{% endfor %}
"""
        };
        
        print(f"[DocGenie] Created {len(templates)} documentation templates");
        report templates=templates;
    }
    
    can generate_architecture_diagram with `root entry {
        if (not config.diagram_enabled) {
            print("[DocGenie] Diagram generation disabled");
            return;
        }
        
        print("[DocGenie] Generating architecture diagram...");
        
        relationships = here.reporter().relationships;
        entities_map = here.reporter().entities_map;
        
        # Create graphviz diagram
        diagram = Digraph(comment='Codebase Architecture');
        diagram.attr(rankdir='TB');
        diagram.attr('node', shape='box', style='rounded,filled');
        
        # Add entity nodes with color coding by type
        type_colors = {
            'class': 'lightblue',
            'function': 'lightgreen', 
            'method': 'lightyellow',
            'module': 'lightcoral',
            'variable': 'lightgray'
        };
        
        for entity_id, entity in entities_map.items() {
            color = type_colors.get(entity.type, 'white');
            label = f"{entity.name}\\n({entity.type})";
            if (entity.complexity > 5.0) {
                label += "\\n⚠️ High Complexity";
            }
            diagram.node(entity_id, label, fillcolor=color);
        }
        
        # Add relationship edges
        for relationship in relationships {
            edge_attrs = {};
            
            # Style edges by relationship type
            if (relationship.relationship_type == "calls") {
                edge_attrs['color'] = 'blue';
                edge_attrs['label'] = 'calls';
            } elif (relationship.relationship_type == "imports") {
                edge_attrs['color'] = 'green';
                edge_attrs['label'] = 'imports';
            } elif (relationship.relationship_type == "inherits") {
                edge_attrs['color'] = 'red';
                edge_attrs['label'] = 'inherits';
            } else {
                edge_attrs['color'] = 'gray';
                edge_attrs['label'] = relationship.relationship_type;
            }
            
            # Only show high-confidence relationships
            if (relationship.confidence > 0.7) {
                diagram.edge(relationship.from_entity, relationship.to_entity, **edge_attrs);
            }
        }
        
        # Render diagram
        diagram_path = f"{config.output_dir}/architecture_diagram";
        diagram.render(diagram_path, format=config.diagram_format, cleanup=True);
        
        print(f"[DocGenie] Architecture diagram saved to {diagram_path}.{config.diagram_format}");
        report architecture_diagram_path=f"{diagram_path}.{config.diagram_format}";
    }
    
    can generate_call_graph with `root entry {
        if (not config.diagram_enabled) {
            print("[DocGenie] Call graph generation disabled");
            return;
        }
        
        print("[DocGenie] Generating call graph diagram...");
        
        relationships = here.reporter().relationships;
        entities_map = here.reporter().entities_map;
        
        # Filter call relationships
        call_relationships = [r for r in relationships if r.relationship_type == "calls"];
        
        if (not call_relationships) {
            print("[DocGenie] No call relationships found for call graph");
            return;
        }
        
        # Create call graph
        call_graph = Digraph(comment='Function Call Graph');
        call_graph.attr(rankdir='LR');
        call_graph.attr('node', shape='ellipse', style='filled');
        
        # Add function nodes
        for relationship in call_relationships {
            if (relationship.confidence > 0.8) {  # Only high-confidence calls
                from_entity = entities_map.get(relationship.from_entity);
                to_entity = entities_map.get(relationship.to_entity);
                
                if (from_entity and from_entity.type == "function") {
                    call_graph.node(relationship.from_entity, from_entity.name);
                }
                if (to_entity and to_entity.type == "function") {
                    call_graph.node(relationship.to_entity, to_entity.name);
                }
                
                call_graph.edge(relationship.from_entity, relationship.to_entity);
            }
        }
        
        # Render call graph
        call_graph_path = f"{config.output_dir}/call_graph";
        call_graph.render(call_graph_path, format=config.diagram_format, cleanup=True);
        
        print(f"[DocGenie] Call graph saved to {call_graph_path}.{config.diagram_format}");
        report call_graph_path=f"{call_graph_path}.{config.diagram_format}";
    }
    
    can synthesize_documentation_sections with `root entry {
        print("[DocGenie] Synthesizing documentation sections...");
        
        entities_map = here.reporter().entities_map;
        relationships = here.reporter().relationships;
        templates = here.reporter().templates;
        
        # Initialize generated document
        generated_doc = GeneratedDocument();
        
        # Get repository metadata
        metadata = ccg_data.get("metadata", {});
        generated_doc.title = metadata.get("repository_name", "Codebase Documentation");
        generated_doc.metadata = {
            "repository_url": repository_info.get("url", ""),
            "generation_date": datetime.datetime.now().isoformat(),
            "analyzer_version": "1.0.0",
            "total_entities": len(entities_map),
            "total_relationships": len(relationships)
        };
        
        # Generate overview section
        overview_section = DocumentationSection(
            section_id="overview",
            title="Repository Overview",
            content="",
            order=1,
            section_type="overview",
            related_entities=list(entities_map.keys())
        );
        
        # Calculate statistics
        entity_types = collections.Counter(entity.type for entity in entities_map.values());
        complexity_values = [entity.complexity for entity in entities_map.values() if entity.complexity > 0];
        avg_complexity = sum(complexity_values) / len(complexity_values) if complexity_values else 0;
        
        # Generate overview content using template
        overview_content = templates["overview"].render(
            repository_name=generated_doc.title,
            repository_url=generated_doc.metadata["repository_url"],
            generation_date=generated_doc.metadata["generation_date"],
            analyzer_version=generated_doc.metadata["analyzer_version"],
            total_files=metadata.get("total_files", 0),
            total_entities=generated_doc.metadata["total_entities"],
            total_relationships=generated_doc.metadata["total_relationships"],
            avg_complexity=f"{avg_complexity:.2f}",
            architecture_summary="Architecture analysis based on code relationships and complexity metrics.",
            structure_summary=f"Detected {len(entity_types)} entity types: {dict(entity_types)}"
        );
        
        overview_section.content = overview_content;
        generated_doc.sections.append(overview_section);
        
        # Generate API reference section
        api_section = DocumentationSection(
            section_id="api_reference",
            title="API Reference",
            content="",
            order=2,
            section_type="api",
            related_entities=[eid for eid, e in entities_map.items() if e.type in ["class", "function", "method"]]
        );
        
        # Categorize entities
        classes = [e for e in entities_map.values() if e.type == "class"];
        functions = [e for e in entities_map.values() if e.type == "function"];
        methods = [e for e in entities_map.values() if e.type == "method"];
        
        # Add methods to classes
        for cls in classes {
            cls.methods = [m for m in methods if m.file_path == cls.file_path];
        }
        
        api_content = templates["api_reference"].render(
            classes=classes,
            functions=functions
        );
        
        api_section.content = api_content;
        generated_doc.sections.append(api_section);
        
        # Generate architecture section
        arch_section = DocumentationSection(
            section_id="architecture",
            title="Architecture Analysis",
            content="",
            order=3,
            section_type="architecture",
            related_entities=list(entities_map.keys())
        );
        
        # Analyze dependency patterns
        dependency_analysis = self.analyze_dependency_patterns(relationships, entities_map);
        complexity_summary = self.analyze_complexity_patterns(entities_map);
        
        arch_content = templates["architecture"].render(
            components_summary=f"System contains {len(classes)} classes, {len(functions)} functions, and {len(methods)} methods.",
            dependency_analysis=dependency_analysis,
            complexity_summary=complexity_summary,
            patterns_summary="Design pattern detection analysis (TBD)"
        );
        
        arch_section.content = arch_content;
        generated_doc.sections.append(arch_section);
        
        print(f"[DocGenie] Generated {len(generated_doc.sections)} documentation sections");
        report generated_doc=generated_doc;
    }
    
    can analyze_dependency_patterns with `root entry {
        relationships = here.reporter().relationships;
        entities_map = here.reporter().entities_map;
        
        # Count relationship types
        rel_types = collections.Counter(r.relationship_type for r in relationships);
        
        # Analyze dependency chains
        import_relationships = [r for r in relationships if r.relationship_type == "imports"];
        call_relationships = [r for r in relationships if r.relationship_type == "calls"];
        
        analysis = f"""
**Relationship Distribution**:
- Import relationships: {rel_types.get('imports', 0)}
- Function calls: {rel_types.get('calls', 0)}
- Inheritance: {rel_types.get('inherits', 0)}
- Containment: {rel_types.get('contains', 0)}

**Key Findings**:
- Most imported modules: {self.get_most_imported_modules(import_relationships, entities_map)}
- Most called functions: {self.get_most_called_functions(call_relationships, entities_map)}
- Dependency depth: {self.calculate_dependency_depth(relationships, entities_map)}
"""
        
        return analysis;
    }
    
    can analyze_complexity_patterns with `root entry {
        entities_map = here.reporter().entities_map;
        
        complexity_values = [e.complexity for e in entities_map.values() if e.complexity > 0];
        
        if (not complexity_values) {
            return "No complexity data available.";
        }
        
        high_complexity = [e for e in entities_map.values() if e.complexity > 10.0];
        medium_complexity = [e for e in entities_map.values() if 5.0 < e.complexity <= 10.0];
        low_complexity = [e for e in entities_map.values() if 0 < e.complexity <= 5.0];
        
        summary = f"""
**Complexity Distribution**:
- High complexity (>10): {len(high_complexity)} entities
- Medium complexity (5-10): {len(medium_complexity)} entities  
- Low complexity (≤5): {len(low_complexity)} entities

**Recommendation**: Consider refactoring {len(high_complexity)} high-complexity entities to improve maintainability.
"""
        
        return summary;
    }
    
    can get_most_imported_modules with `root entry {
        import_relationships = args[0];
        entities_map = args[1];
        
        # Count imports per module
        import_counts = {};
        for rel in import_relationships {
            target_entity = entities_map.get(rel.to_entity);
            if (target_entity and target_entity.type == "module") {
                import_counts[target_entity.name] = import_counts.get(target_entity.name, 0) + 1;
            }
        }
        
        # Return top 5 most imported modules
        top_imports = sorted(import_counts.items(), key=lambda x: x[1], reverse=True)[:5];
        return ", ".join([f"{name} ({count} imports)" for name, count in top_imports]) if top_imports else "None detected";
    }
    
    can get_most_called_functions with `root entry {
        call_relationships = args[0];
        entities_map = args[1];
        
        # Count calls per function
        call_counts = {};
        for rel in call_relationships {
            target_entity = entities_map.get(rel.to_entity);
            if (target_entity and target_entity.type in ["function", "method"]) {
                call_counts[target_entity.name] = call_counts.get(target_entity.name, 0) + 1;
            }
        }
        
        # Return top 5 most called functions
        top_calls = sorted(call_counts.items(), key=lambda x: x[1], reverse=True)[:5];
        return ", ".join([f"{name} ({count} calls)" for name, count in top_calls]) if top_calls else "None detected";
    }
    
    can calculate_dependency_depth with `root entry {
        relationships = args[0];
        entities_map = args[1];
        
        # Build dependency graph and calculate longest path
        dependency_graph = collections.defaultdict(list);
        
        for rel in relationships {
            if (rel.relationship_type in ["imports", "calls"]) {
                dependency_graph[rel.from_entity].append(rel.to_entity);
            }
        }
        
        # Calculate longest path using DFS
        def dfs(node, visited, path_length):
            if (node in visited) {
                return path_length;
            }
            
            visited.add(node);
            max_depth = path_length;
            
            for neighbor in dependency_graph[node] {
                if (neighbor in entities_map) {
                    depth = dfs(neighbor, visited, path_length + 1);
                    max_depth = max(max_depth, depth);
                }
            }
            
            return max_depth;
        
        max_depth = 0;
        for entity_id in entities_map.keys() {
            if (entity_id not in dependency_graph) {
                continue;
            }
            depth = dfs(entity_id, set(), 0);
            max_depth = max(max_depth, depth);
        }
        
        return max_depth;
    }
    
    can add_code_citations with `root entry {
        print("[DocGenie] Adding code citations and cross-references...");
        
        generated_doc = here.reporter().generated_doc;
        entities_map = here.reporter().entities_map;
        relationships = here.reporter().relationships;
        
        # Build citation index
        citations = {};
        
        # Add entity citations
        for entity_id, entity in entities_map.items() {
            citations[entity_id] = {
                "title": entity.name,
                "type": entity.type,
                "file_path": entity.file_path,
                "line_range": f"lines {entity.start_line}-{entity.end_line}",
                "url": f"{repository_info.get('url', '')}/blob/main/{entity.file_path}#L{entity.start_line}-L{entity.end_line}"
            };
        }
        
        # Add relationship citations
        for rel in relationships {
            if (rel.confidence > 0.8) {
                citations[f"{rel.from_entity}->{rel.to_entity}"] = {
                    "type": "relationship",
                    "from": rel.from_entity,
                    "to": rel.to_entity,
                    "relationship_type": rel.relationship_type,
                    "confidence": rel.confidence
                };
            }
        }
        
        generated_doc.citations = citations;
        
        print(f"[DocGenie] Added {len(citations)} citations and cross-references");
    }
    
    can generate_final_document with `root entry {
        print("[DocGenie] Generating final documentation document...");
        
        generated_doc = here.reporter().generated_doc;
        config = here.config;
        
        # Ensure output directory exists
        pathlib.Path(config.output_dir).mkdir(parents=True, exist_ok=True);
        
        # Combine all sections into final document
        final_content = f"# {generated_doc.title}\n\n";
        final_content += f"**Generated**: {generated_doc.metadata['generation_date']}\n";
        final_content += f"**Repository**: {generated_doc.metadata['repository_url']}\n\n";
        
        # Add table of contents
        final_content += "## Table of Contents\n\n";
        for section in sorted(generated_doc.sections, key=lambda x: x.order) {
            final_content += f"- [{section.title}](#{section.section_id})\n";
        }
        final_content += "\n---\n\n";
        
        # Add all sections
        for section in sorted(generated_doc.sections, key=lambda x: x.order) {
            final_content += section.content;
            final_content += "\n---\n\n";
        }
        
        # Add citations section
        final_content += "## Citations and References\n\n";
        final_content += "This documentation includes cross-references to the following code entities:\n\n";
        
        entity_citations = {k: v for k, v in generated_doc.citations.items() if "->" not in k};
        for entity_id, citation in entity_citations.items() {
            final_content += f"- **{citation['title']}** ({citation['type']}) - {citation['file_path']} ({citation['line_range']})\n";
        }
        
        # Save final document
        output_file = f"{config.output_dir}/documentation.md";
        with open(output_file, 'w', encoding='utf-8') as f {
            f.write(final_content);
        }
        
        print(f"[DocGenie] Final documentation saved to {output_file}");
        report final_document_path=output_file;
    }
    
    can generate_html_output with `root entry {
        print("[DocGenie] Generating HTML documentation...");
        
        generated_doc = here.reporter().generated_doc;
        config = here.config;
        
        # Create HTML template
        html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ doc_title }}</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; max-width: 1200px; margin: 0 auto; padding: 20px; line-height: 1.6; }
        h1, h2, h3 { color: #2c3e50; }
        pre { background: #f8f9fa; padding: 15px; border-radius: 5px; overflow-x: auto; }
        code { background: #e9ecef; padding: 2px 5px; border-radius: 3px; }
        .toc { background: #f8f9fa; padding: 20px; border-radius: 5px; margin-bottom: 30px; }
        .citation { background: #e7f3ff; padding: 10px; border-left: 4px solid #007bff; margin: 10px 0; }
        .section { margin-bottom: 40px; }
    </style>
</head>
<body>
    <h1>{{ doc_title }}</h1>
    <div class="toc">
        <h2>Table of Contents</h2>
        <ul>
        {% for section in sections %}
            <li><a href="#{{ section.section_id }}">{{ section.title }}</a></li>
        {% endfor %}
        </ul>
    </div>
    
    {% for section in sections %}
    <div class="section" id="{{ section.section_id }}">
        {{ section.content | replace('\n', '<br>') | replace('# ', '<h2>') | replace('## ', '<h3>') | replace('### ', '<h4>') | replace('**', '<strong>') | replace('**', '</strong>') }}
    </div>
    <hr>
    {% endfor %}
    
    <div class="citation">
        <h2>Citations</h2>
        <p>This documentation was generated automatically. Cross-references are available for all documented entities.</p>
    </div>
</body>
</html>
        """;
        
        # Render HTML
        template = jinja2.Template(html_template);
        html_content = template.render(
            doc_title=generated_doc.title,
            sections=generated_doc.sections
        );
        
        # Save HTML file
        html_file = f"{config.output_dir}/documentation.html";
        with open(html_file, 'w', encoding='utf-8') as f {
            f.write(html_content);
        }
        
        print(f"[DocGenie] HTML documentation saved to {html_file}");
        report html_document_path=html_file;
    }
    
    can validate_documentation_quality with `root entry {
        print("[DocGenie] Validating documentation quality...");
        
        generated_doc = here.reporter().generated_doc;
        
        quality_metrics = {
            "total_sections": len(generated_doc.sections),
            "total_citations": len(generated_doc.citations),
            "has_overview": any(s.section_type == "overview" for s in generated_doc.sections),
            "has_api_reference": any(s.section_type == "api" for s in generated_doc.sections),
            "has_architecture": any(s.section_type == "architecture" for s in generated_doc.sections),
            "sections_with_content": len([s for s in generated_doc.sections if s.content.strip()]),
            "quality_score": 0.0
        };
        
        # Calculate quality score
        score = 0.0;
        if (quality_metrics["total_sections"] >= 3) score += 0.3;
        if (quality_metrics["has_overview"]) score += 0.2;
        if (quality_metrics["has_api_reference"]) score += 0.2;
        if (quality_metrics["has_architecture"]) score += 0.2;
        if (quality_metrics["total_citations"] > 0) score += 0.1;
        
        quality_metrics["quality_score"] = score;
        
        print(f"[DocGenie] Quality metrics: {quality_metrics}");
        return quality_metrics;
    }
    
    can generate_documentation with `root entry {
        print("🚀 DocGenie Agent: Starting documentation generation...");
        
        # Step 1: Initialize configuration
        self.initialize_config();
        
        # Step 2: Validate CCG data
        self.validate_ccg_data();
        
        # Step 3: Analyze entities and relationships
        self.analyze_code_entities();
        self.analyze_relationships();
        
        # Step 4: Create documentation templates
        self.create_documentation_templates();
        
        # Step 5: Generate diagrams (if enabled)
        if (config.diagram_enabled) {
            self.generate_architecture_diagram();
            self.generate_call_graph();
        }
        
        # Step 6: Synthesize documentation sections
        self.synthesize_documentation_sections();
        
        # Step 7: Add citations and cross-references
        self.add_code_citations();
        
        # Step 8: Generate final outputs
        self.generate_final_document();
        self.generate_html_output();
        
        # Step 9: Validate quality
        quality_metrics = self.validate_documentation_quality();
        
        print("✅ DocGenie Agent: Documentation generation completed successfully!");
        
        return {
            "status": "completed",
            "output_files": [
                here.reporter().final_document_path,
                here.reporter().html_document_path
            ],
            "quality_metrics": quality_metrics,
            "summary": {
                "total_entities_processed": len(here.reporter().entities_map),
                "total_relationships_analyzed": len(here.reporter().relationships),
                "sections_generated": len(generated_doc.sections),
                "citations_added": len(generated_doc.citations)
            }
        };
    }
}
