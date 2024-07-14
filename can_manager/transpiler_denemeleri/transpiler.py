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
            shape_data['outputDataTypes'] = {}
            for type_elem in shape.find('outputDataTypes').findall('type'):
                shape_data['outputDataTypes'][type_elem.get('pin')] = type_elem.text
        elif shape_data['type'] == 'parallelogram':
            shape_data['outputData'] = {}
            for pin in shape.find('outputData').findall('pin'):
                shape_data['outputData'][pin.get('number')] = pin.text
            shape_data['outputDataTypes'] = {}
            for type_elem in shape.find('outputDataTypes').findall('type'):
                shape_data['outputDataTypes'][type_elem.get('pin')] = type_elem.text
        elif shape_data['type'] == 'ellipse':
            shape_data['outputDataTypes'] = {}
            output_data_types = shape.find('outputDataTypes')
            if output_data_types is not None:
                for type_elem in output_data_types.findall('type'):
                    shape_data['outputDataTypes'][type_elem.get('pin')] = type_elem.text

        shapes.append(shape_data)

        for conn in shape.find('connections').findall('connection'):
            connections.append({
                'from': conn.get('startPin'),
                'to': conn.get('endPin')
            })

    return shapes, connections

def cpp_type(xml_type):
    type_map = {
        'int8_t': 'int8_t',
        'uint8_t': 'uint8_t',
        'int16_t': 'int16_t',
        'uint16_t': 'uint16_t',
        'int32_t': 'int32_t',
        'uint32_t': 'uint32_t',
        'int64_t': 'int64_t',
        'uint64_t': 'uint64_t',
        'float': 'float',
        'double': 'double',
        'long double': 'long double',
        'bool': 'bool',
        'char': 'char',
        'unsigned char': 'unsigned char',
        'short': 'short',
        'unsigned short': 'unsigned short',
        'int': 'int',
        'unsigned int': 'unsigned int',
        'long': 'long',
        'unsigned long': 'unsigned long',
        'long long': 'long long',
        'unsigned long long': 'unsigned long long'
    }
    return type_map.get(xml_type, 'auto')  # 'auto' as fallback for unknown types

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

template<typename T, size_t M>
T extract_bits(T input, int start, int end) {
    T mask = ((static_cast<T>(1) << (end - start + 1)) - 1) << start;
    return (input & mask) >> start;
}

"""

    for shape in shapes:
        if shape['type'] == 'rectangle':
            code += f"class {shape['name']} {{\npublic:\n"
            for i, pin in shape['pinData'].items():
                output_type = cpp_type(shape['outputDataTypes'][i])
                if output_type in ['float', 'double', 'long double']:
                    code += f"    {output_type} output{i};\n"
                else:
                    bit_width = pin['endBit'] - pin['startBit'] + 1
                    code += f"    std::bitset<{bit_width}> output{i};\n"
            code += f"    std::string id;\n"
            code += f"    bool isStd;\n"
            code += f"    {shape['name']}() {{\n"
            code += f"        id = \"{shape['id']}\";\n"
            code += f"        isStd = {str(shape['isStd']).lower()};\n"
            code += "    }\n"
            for i, pin in shape['pinData'].items():
                output_type = cpp_type(shape['outputDataTypes'][i])
                code += f"    {output_type} get_output{i}() const {{\n"
                if output_type in ['float', 'double', 'long double']:
                    code += f"        return output{i};\n"
                else:
                    bit_width = pin['endBit'] - pin['startBit'] + 1
                    code += f"        return static_cast<{output_type}>(extract_bits<{output_type}, {bit_width}>(output{i}.to_ullong(), {pin['startBit']}, {pin['endBit']}));\n"
                code += "    }\n"
            code += "};\n\n"
            
    for shape in shapes:
        if shape['type'] == 'parallelogram':
            input_params = ", ".join([f"{cpp_type(shape['outputDataTypes']['1'])} input{i}" for i in range(1, shape['inputCount'] + 1)])
            output_type = cpp_type(shape['outputDataTypes']['1'])
            code += f"{output_type} {shape['name']}({input_params}) {{\n"
            for i in range(1, shape['outputCount'] + 1):
                output_expr = shape['outputData'][str(i)]
                parsed_expr = parse_output_expression(output_expr)
                code += f"    {output_type} output{i} = {parsed_expr};\n"
            code += f"    return output1;\n}}\n\n"

    for shape in shapes:
        if shape['type'] == 'ellipse':
            if shape['outputDataTypes']:
                output_type = cpp_type(next(iter(shape['outputDataTypes'].values())))
            else:
                output_type = 'double'  # Default to double if no type is specified
            code += f"{output_type} {shape['name']};\n"

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
            input_params = ", ".join([f"{from_shape_data['name'].lower()}.get_output{from_pin + 1}()" for _ in range(to_shape_data['inputCount'])])
            result_var = f"result_{to_shape_data['name']}_{to_pin}"
            result_vars.add(result_var)
            output_type = cpp_type(to_shape_data['outputDataTypes']['1'])
            code += f"    {output_type} {result_var} = {to_shape_data['name']}({input_params});\n"
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