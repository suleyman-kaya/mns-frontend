import xml.etree.ElementTree as ET
import re

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
            'inputCount': int(shape.get('inputCount')),
            'outputCount': int(shape.get('outputCount')),
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
            shape_data['inputPinTypes'] = shape.find('inputPinTypes').text.split(',')
            shape_data['outputPinTypes'] = shape.find('outputPinTypes').text.split(',')
        
        shapes.append(shape_data)
        
        for conn in shape.find('connections').findall('connection'):
            connections.append({
                'from': conn.get('startPin'),
                'to': conn.get('endPin')
            })
    
    return shapes, connections

def parse_output_expression(expr):
    tokens = re.findall(r'i\d+(?:\[\d+:\d+\])?|\+', expr)
    cpp_expr = []
    for token in tokens:
        if token == '+':
            cpp_expr.append(token)
        elif '[' in token:
            input_num, bit_range = token.split('[')
            input_num = int(input_num[1:])
            start, end = map(int, bit_range[:-1].split(':'))
            mask = ((1 << (end - start)) - 1) << start
            cpp_expr.append(f"((input{input_num} & {mask}) >> {start})")
        else:
            input_num = int(token[1:])
            cpp_expr.append(f"input{input_num}")
    return " ".join(cpp_expr)

def generate_cpp_code(shapes, connections):
    code = "#include <iostream>\n#include <string>\n#include <vector>\n\n"
    
    # Generate classes for rectangles
    for shape in shapes:
        if shape['type'] == 'rectangle':
            code += f"class {shape['name']} {{\npublic:\n"
            for i in range(1, shape['outputCount'] + 1):
                code += f"    int output{i};\n"
            code += f"    {shape['name']}() {{\n"
            for i in range(1, shape['outputCount'] + 1):
                start_bit = shape['pinData'][str(i)]['startBit']
                end_bit = shape['pinData'][str(i)]['endBit']
                code += f"        output{i} = 0; // Bits {start_bit}-{end_bit}\n"
            code += "    }\n};\n\n"
    
    # Generate functions for parallelograms
    for shape in shapes:
        if shape['type'] == 'parallelogram':
            input_params = ", ".join([f"int input{i}" for i in range(1, shape['inputCount'] + 1)])
            code += f"int {shape['name']}({input_params}) {{\n"
            for i in range(1, shape['outputCount'] + 1):
                output_expr = shape['outputData'][str(i)]
                parsed_expr = parse_output_expression(output_expr)
                code += f"    int output{i} = {parsed_expr};\n"
            code += f"    return output1;\n}}\n\n"
    
    # Generate variables for ellipses
    for shape in shapes:
        if shape['type'] == 'ellipse':
            type_str = 'int' if shape['inputPinTypes'][0] == 'true' else 'signed int'
            code += f"{type_str} {shape['name']};\n"
    
    code += "\n"
    
    # Generate main function
    code += "int main() {\n"
    
    # Instantiate classes
    for shape in shapes:
        if shape['type'] == 'rectangle':
            code += f"    {shape['name']} {shape['name'].lower()};\n"
    
    code += "\n"
    
    # Generate connections
    result_vars = set()
    for conn in connections:
        from_shape, from_pin = map(int, conn['from'].split(','))
        to_shape, to_pin = map(int, conn['to'].split(','))
        
        from_shape_data = shapes[from_shape]
        to_shape_data = shapes[to_shape]
        
        if from_shape_data['type'] == 'rectangle' and to_shape_data['type'] == 'parallelogram':
            input_params = ", ".join([f"{from_shape_data['name'].lower()}.output{from_pin + 1}" for _ in range(to_shape_data['inputCount'])])
            result_var = f"result_{to_shape_data['name']}_{to_pin}"
            result_vars.add(result_var)
            code += f"    int {result_var} = {to_shape_data['name']}({input_params});\n"
        elif from_shape_data['type'] == 'parallelogram' and to_shape_data['type'] == 'ellipse':
            result_var = f"result_{from_shape_data['name']}_{from_pin}"
            if result_var in result_vars:
                code += f"    {to_shape_data['name']} = {result_var};\n"
            else:
                code += f"    // Warning: {result_var} not defined before use\n"
                code += f"    // {to_shape_data['name']} = {result_var};\n"
    
    code += "\n    return 0;\n}\n"
    
    return code

# Main execution
xml_file = 'schema.xml'  # XML dosyasının adını burada belirtin
shapes, connections = parse_xml(xml_file)
cpp_code = generate_cpp_code(shapes, connections)

# C++ kodunu bir dosyaya yazma
with open('output.cpp', 'w') as f:
    f.write(cpp_code)

print("C++ kodu 'output.cpp' dosyasına yazıldı.")