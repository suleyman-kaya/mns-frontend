import xml.etree.ElementTree as ET
import re, sys

def parse_xml(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()
    shapes = []
    connections = []

    for shape in root.findall('shape'):
        shape_data = {
            'type': shape.get('type'),
            'name': shape.get('name'),
            'id': shape.get('id', ''),
            'inputCount': int(shape.get('inputCount', 0)),
            'outputCount': int(shape.get('outputCount', 0)),
        }

        if shape_data['type'] == 'rectangle':
            shape_data['isStd'] = shape.get('isStd') == 'true'
            shape_data['pinData'] = {}
            for pin in shape.find('pinData').findall('pin'):
                shape_data['pinData'][pin.get('number')] = {
                    'startBit': int(pin.get('startBit')),
                    'endBit': int(pin.get('endBit'))
                }
        elif shape_data['type'] == 'parallelogram':
            shape_data['outputData'] = {}
            for pin in shape.find('outputData').findall('pin'):
                shape_data['outputData'][pin.get('number')] = pin.text
        elif shape_data['type'] == 'ellipse':
            shape_data['inputPinTypes'] = shape.find('inputPinTypes').text == 'true'
            shape_data['outputPinTypes'] = shape.find('outputPinTypes').text == 'true'

        shapes.append(shape_data)

        for conn in shape.find('connections').findall('connection'):
            connections.append({
                'from': conn.get('startPin'),
                'to': conn.get('endPin')
            })

    return shapes, connections

def parse_output_expression(expr):
    tokens = re.findall(r'i\d+(?:\[\d+:\d+\])?|[-+]', expr)
    cpp_expr = []
    for token in tokens:
        if token in ['+', '-']:
            cpp_expr.append(token)
        elif '[' in token:
            input_num, bit_range = token.split('[')
            input_num = int(input_num[1:])
            start, end = map(int, bit_range[:-1].split(':'))
            cpp_expr.append(f"extract_bits<{end-start+1}>({input_num}, {start}, {end})")
        else:
            input_num = int(token[1:])
            cpp_expr.append(f"input{input_num}")
    return " ".join(cpp_expr)

def generate_cpp_code(shapes, connections):
    code = """#include <iostream>
#include <string>
#include <vector>
#include <bitset>
#include <cstdint>

template<size_t M>
uint64_t extract_bits(uint64_t input, int start, int end) {
    uint64_t mask = ((1ULL << (end - start + 1)) - 1) << start;
    return (input & mask) >> start;
}

"""

    for shape in shapes:
        if shape['type'] == 'rectangle':
            max_bit = max(pin['endBit'] for pin in shape['pinData'].values())
            code += f"class {shape['name']} {{\npublic:\n"
            code += f"    std::bitset<{max_bit + 1}> output;\n"
            code += f"    {shape['name']}() {{\n"
            code += "        output.reset();\n"
            code += "    }\n"
            for i, pin in shape['pinData'].items():
                bit_width = pin['endBit'] - pin['startBit'] + 1
                code += f"    std::bitset<{bit_width}> get_output{i}() const {{\n"
                code += f"        return extract_bits<{bit_width}>(output.to_ullong(), {pin['startBit']}, {pin['endBit']});\n"
                code += "    }\n"
            code += "};\n\n"

    for shape in shapes:
        if shape['type'] == 'parallelogram':
            input_params = ", ".join([f"uint64_t input{i}" for i in range(1, shape['inputCount'] + 1)])
            code += f"uint64_t {shape['name']}({input_params}) {{\n"
            for i in range(1, shape['outputCount'] + 1):
                output_expr = shape['outputData'][str(i)]
                parsed_expr = parse_output_expression(output_expr)
                code += f"    uint64_t output{i} = {parsed_expr};\n"
            code += f"    return output1;\n}}\n\n"

    for shape in shapes:
        if shape['type'] == 'ellipse':
            type_str = 'uint64_t' if shape['inputPinTypes'] else 'int64_t'
            code += f"{type_str} {shape['name']};\n"

    code += "\nint main() {\n"

    for shape in shapes:
        if shape['type'] == 'rectangle':
            code += f"    {shape['name']} {shape['name'].lower()};\n"

    code += "\n"

    result_vars = set()
    for conn in connections:
        from_shape, from_pin = map(int, conn['from'].split(','))
        to_shape, to_pin = map(int, conn['to'].split(','))

        from_shape_data = shapes[from_shape]
        to_shape_data = shapes[to_shape]

        if from_shape_data['type'] == 'rectangle' and to_shape_data['type'] == 'parallelogram':
            input_params = ", ".join([f"{from_shape_data['name'].lower()}.get_output{from_pin + 1}().to_ullong()" for _ in range(to_shape_data['inputCount'])])
            result_var = f"result_{to_shape_data['name']}_{to_pin}"
            result_vars.add(result_var)
            code += f"    uint64_t {result_var} = {to_shape_data['name']}({input_params});\n"
        elif from_shape_data['type'] == 'parallelogram' and to_shape_data['type'] == 'ellipse':
            result_var = f"result_{from_shape_data['name']}_{from_pin}"
            if result_var in result_vars:
                code += f"    {to_shape_data['name']} = {result_var};\n"
            else:
                code += f"    // Warning: {result_var} not defined before use\n"
                code += f"    // {to_shape_data['name']} = {result_var};\n"

    code += "\n    return 0;\n}\n"

    return code

if len(sys.argv) != 2:
    print("Usage: python3 transpiler.py <Your_CAN_Manager_Scheme.xml>")
else:
    file_path = sys.argv[1]
    # Main execution
    xml_file = file_path
    shapes, connections = parse_xml(xml_file)
    cpp_code = generate_cpp_code(shapes, connections)

    # Write C++ code to a file
    with open('output.cpp', 'w') as f:
        f.write(cpp_code)

    print("Generated C++ code and saved as 'output.cpp'.")