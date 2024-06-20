import re

# Define the regex patterns
class_pattern = re.compile(r'^\s*class\s+(?P<class_name>\w+)\s*[\(:]?')
function_pattern = re.compile(r'^\s*def\s+(?P<function_name>\w+)\s*\((?P<parameters>[^\)]*)\)\s*:')
service_pattern = re.compile(r'^\s*(?P<service_name>\w+)\s*=\s*(?P<class_instance>\w+)\(\s*\)')

filename = input("Enter file name: ")
class_functions = {}
service_class_mapping = {}
with open(filename, 'r') as f:
    for line in f:
        class_match = class_pattern.match(line)
        function_match = function_pattern.match(line)
        service_match = service_pattern.match(line)

        if class_match:
            current_class = class_match.group('class_name')
            if current_class not in class_functions:
                class_functions[current_class] = {}
            print(f"Class name: {current_class}")

        if function_match:
            function_name = function_match.group('function_name')
            parameters = function_match.group('parameters')
            if current_class:
                parameters_split = parameters.split(',')[1:]
                parameters_split = [param.strip() for param in parameters_split]
                parameters = ', '.join(parameters_split)
                class_functions[current_class][function_name] = parameters
                print(f"  Function name: {function_name} (in class {current_class})")
            else:
                print(f"Function name: {function_name} (standalone)")

        if service_match:
            service_name = service_match.group('service_name')
            class_instance = service_match.group('class_instance')
            service_class_mapping[service_name] = class_instance
            print(f"Service name: {service_name}, Class instance: {class_instance}")


print(class_functions, service_class_mapping)
