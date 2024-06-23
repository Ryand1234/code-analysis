import re
"""
# Define the regex patterns
class_pattern = re.compile(r'^\s*class\s+(?P<class_name>\w+)\s*[\(:]?')
function_pattern = re.compile(r'^\s*def\s+(?P<function_name>\w+)\s*\((?P<parameters>[^\)]*)\)\s*:')
service_pattern = re.compile(r'^\s*(?P<service_name>\w+)\s*=\s*(?P<class_instance>\w+)\(\s*\)')
self_function_pattern = re.compile(r'self\.(?P<self_function>\w+)\s*\(')
super_function_pattern = re.compile(r'super\(\)\.(?P<super_function>\w+)\s*\(')
instance_function_pattern = re.compile(r'(?P<instance>\w+)\.(?P<instance_function>\w+)\s*\(')
"""

class_pattern = re.compile(r'^\s*class\s+(?P<class_name>\w+)\s*[\(:]?')
function_pattern = re.compile(r'^\s*def\s+(?P<function_name>\w+)\s*\((?P<parameters>[^\)]*)\)\s*:')
service_pattern = re.compile(r'^\s*(?P<service_name>\w+)\s*=\s*(?P<class_instance>\w+)\(\s*\)')
self_function_pattern = re.compile(r'self\.(?P<self_function>\w+)\s*\(')
super_function_pattern = re.compile(r'super\(\)\.(?P<super_function>\w+)\s*\(')
instance_function_pattern = re.compile(r'(?P<instance>\w+)\.(?P<instance_function>\w+)\s*\(')


def change(service):    
    service_s = service.split('_')
    if len(service_s) == 1:
        return service
    nservice = ""#service_s.capitalize()
    for word in service_s:
        nservice += word.capitalize()
    return nservice

def check(service, classname):
    nservice = change(service)
    print(nservice, classname)
    return nservice == classname

dirname = input("Enter directory name: ")
class_functions = {}
class_functions_set = {}
service_class_mapping = {}
functions_used_service = {}
import os
for file in os.listdir(dirname):
    filename = os.path.join(dirname, file)
    if not filename.endswith('.py'):
        continue
    functions_in_class = []
    functions_used = set()
    with open(filename, 'r') as f:
        for line in f:
            class_match = class_pattern.match(line)
            function_match = function_pattern.match(line)
            service_match = service_pattern.match(line)
            self_function_match = self_function_pattern.search(line)
            super_function_match = super_function_pattern.search(line)
            instance_function_match = instance_function_pattern.search(line)
    
            if class_match:
                current_class = class_match.group('class_name')
                if current_class not in class_functions:
                    class_functions[current_class] = {}
                    class_functions_set[current_class] = set()
                if current_class not in functions_used_service:
                    functions_used_service[current_class] = set()
                print(f"Class name: {current_class}")
                functions_in_class = []

            if function_match:
                function_name = function_match.group('function_name')
                parameters = function_match.group('parameters')
                if current_class:
                    functions_in_class.append(function_name)
                    parameters_split = parameters.split(',')[1:]
                    parameters_split = [param.strip() for param in parameters_split]
                    parameters = ', '.join(parameters_split)
                    class_functions[current_class][function_name] = parameters
                    class_functions_set[current_class].add(function_name)
                    print(f"  Function name: {function_name} (in class {current_class})")
                else:
                    print(f"Function name: {function_name} (standalone)")
    
            if service_match:
                service_name = service_match.group('service_name')
                class_instance = service_match.group('class_instance')
                if check(service_name, class_instance):
                    service_class_mapping[service_name] = class_instance
                    service_class_mapping[class_instance] = service_name
                    print(f"Service name: {service_name}, Class instance: {class_instance}")
        
            if self_function_match:
                self_function = self_function_match.group('self_function')
                functions_used_service[current_class].add(self_function)
                print(f"  Self function call: {self_function} (in class {current_class})")

            if super_function_match:
                super_function = super_function_match.group('super_function')
                print(f"  Super function call: {super_function} (in class {current_class})")

            if instance_function_match and instance_function_match.group('instance') not in functions_in_class:
                instance = instance_function_match.group('instance')
                instance_function = instance_function_match.group('instance_function')
                if instance == 'self':
                    functions_used.add(instance_function)
                    instance = current_class
                if instance not in functions_used_service:
                    functions_used_service[instance] = set()
                functions_used_service[instance].add(instance_function)

                print(f"  Instance function call: {instance_function} (from instance {instance})")

service_names = [key for key, value in service_class_mapping.items()]

final = {}
functions_not_used = {}
unknown_functions = {}
for k in service_names:
    if k not in functions_used_service:
        continue
    cur = change(k)
    if cur not in final:
        final[cur] = set()
    final[cur].update(functions_used_service[k])

for k, value in class_functions_set.items():
    if k not in final:
        continue
    if k not in functions_not_used:
        functions_not_used[k] = {}
    cur = value - final[k]
    for f in cur:
        functions_not_used[k][f] = class_functions[k][f]


for k, value in final.items():
    if k not in final:
        continue
    if k not in unknown_functions:
        unknown_functions[k] = set()
    unknown_functions[k] = value - class_functions_set[k]

#print(class_functions, service_class_mapping)
print("###########################################################################################")
print("######################   GENERATING REPORT          #######################################")
print("###########################################################################################")
for k, v in functions_not_used.items():
    print("#####\tClassName: ", k)
    for f, p in v.items():
        print("#####\t\tFunction Name: ", f, "(", p, ")")
print("##########################################################################################")
print("############################   UNKNOWN FUNCTIONS    ######################################")
print("##########################################################################################")
for k, v in unknown_functions.items():
    print("#####\tClassName: ", k)
    for f in v:
        print("#####\t\tFunction Name: ", f)
