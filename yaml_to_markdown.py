import yaml

def yaml_to_markdown(yaml_file, md_file):
    with open(yaml_file, 'r') as yf, open(md_file, 'w') as mf:
        yaml_content = yaml.safe_load(yf)
        mf.write("# YAML Mapping Documentation\n\n")
        for section, mappings in yaml_content.items():
            mf.write(f"## {section} Mappings\n\n")
            mf.write("```yaml\n")
            yaml.dump({section: mappings}, mf, default_flow_style=False)
            mf.write("```\n\n")

# def yaml_to_dot(yaml_file, dot_file):
#     with open(yaml_file, 'r') as yf, open(dot_file, 'w') as df:
#         yaml_content = yaml.safe_load(yf)
#         df.write("digraph Mappings {\n")
#         df.write("    node [shape=box];\n")
#         for section, mappings in yaml_content.items():
#             for source, config in mappings.get('mappings', {}).items():
#                 if 'target' in config:
#                     df.write(f'    "{source}" -> "{config["target"]}";\n')
#                 elif 'targets' in config:
#                     for target in config['targets']:
#                         df.write(f'    "{source}" -> "{target}";\n')
#             df.write("}\n")

# def yaml_to_mermaid(yaml_file, md_file):
#     with open(yaml_file, 'r') as yf, open(md_file, 'w') as mf:
#         yaml_content = yaml.safe_load(yf)
#         mf.write("```mermaid\n")
#         mf.write("graph TD;\n")
#         for section, mappings in yaml_content.items():
#             for source, config in mappings.get('mappings', {}).items():
#                 if 'target' in config:
#                     mf.write(f'    "{source}" --> "{config["target"]}";\n')
#                 elif 'targets' in config:
#                     for target in config['targets']:
#                         mf.write(f'    "{source}" --> "{target}";\n')
#         mf.write("```\n")

if __name__ == "__main__":
    yaml_to_markdown('mapping_spec.yaml', 'mapping_spec.md')
    # yaml_to_dot('mapping_spec.yaml', 'mappings.dot')
    # yaml_to_mermaid('mapping_spec.yaml', 'mappings.md')