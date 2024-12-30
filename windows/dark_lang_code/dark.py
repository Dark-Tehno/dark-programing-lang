import math
import re
from .mod import initialize_moduls
from .classes import VariableError, CommandError, SyntaxError, IntVariable, StrVariable, ListVariable, DictVariable, BoolVariable, FloatVariable, get_mod
import os

class CommandProcessor:
    def __init__(self, variable_store, block_store):
        self.variable_store = variable_store
        self.block_store = block_store
        self.mods = {}
        self.is_if = False
        self.if_condition = None
        self.is_block = False
        self.name_block = None


    def from_import_block(self, file, block_name):
        if not os.path.isfile(file):
            raise CommandError(f"File '{file}' not found.")

        with open(file, 'r') as file:
            lines = file.readlines()
        for line in lines:
            if line.startswith(f'set block {block_name} => '):
                self.block_store.add_block(block_name, line.split('=>')[1].strip())
                return ''


    def from_import_variable(self, file, variable_name):
        if not os.path.isfile(file):
            raise CommandError(f"File '{file}' not found.")

        with open(file, 'r') as f:
            lines = f.readlines()
        for line in lines:
            if any(line.startswith(f'set {var_type} {variable_name} ') for var_type in ["int", "str", "list", "dict", "bool", "float"]):
                parts = line.split(' ')
                var_type = parts[1]
                name = parts[2]
                value = ' '.join(parts[3:])
                self.set_variable(var_type, name, value)
                return ''


    def output(self, *args):
        output_string = ' '.join(args)
        output_string = output_string.replace('\\n', '\n').replace('\\s', ' ')
        output_string = re.sub(r'\[\{(.*?)\}\]', lambda match: str(self.variable_store.get_variable(match.group(1).strip()).value), output_string)
        output_string = re.sub(r'\[\{\s*', '[{', output_string)
        output_string = re.sub(r'\s*\}\]', '}]', output_string)
        return output_string.strip()

    def set_variable(self, var_type: str, name_value: str, output: bool = False) -> str:
        try:
            match = re.match(r'^\s*(.*?)\s*:=\s*(.*?)\s*$', name_value)
            name, value = match.groups()
            value = value.replace('\\n', '\n').replace('\\s', ' ')

            if var_type == "int":
                variable = IntVariable(name, value)
            elif var_type == "str":
                variable = StrVariable(name, value)
            elif var_type == "list":
                value = value.split('|')
                variable = ListVariable(name, value)
            elif var_type == "dict":
                pairs = value.split('|')
                dict_value = {}
                for pair in pairs:
                    key, val = pair.split('=>')
                    dict_value[key.strip()] = val.strip()
                variable = DictVariable(name, dict_value)
            elif var_type == "bool":
                if value == "true" or value == "True" or value == 1 or value == '1':
                    variable = BoolVariable(name, True)
                else:
                    variable = BoolVariable(name, False)
            elif var_type == "float":
                variable = FloatVariable(name, float(value))
            else:
                raise VariableError(f"Unknown variable type '{var_type}'.")

            self.variable_store.add_variable(variable)
            return f"Variable '{name}' set." if output else None
        except Exception as e:
            raise VariableError(f"Error setting variable: {e}")

    def delete_variable(self, name, output=False):
        if self.variable_store.delete_variable(name):
            if output:
                return f"Variable '{name}' deleted."
        else:
            raise VariableError(f"Variable '{name}' not found.")

    def input_variable(self, var_type, name, prompt):
        prompt = prompt.replace('\\n', '\n').replace('\\s', ' ')
        value = input(prompt)
        name_value = name + ':=' + value
        return self.set_variable(var_type, name_value)

    def set_if(self, condition, line_number):
        condition = condition.strip()
        condition = re.sub(r'\[\{(.*?)\}\]', lambda match: str(self.variable_store.get_variable(match.group(1).strip()).value), condition)
        condition = re.sub(r'\[\{\s*', '[{', condition)
        condition = re.sub(r'\s*\}\]', '}]', condition)
        self.if_condition = condition

        self.is_if = True
        return None

    def processing_if(self, command_if, line_number):
        condition = self.if_condition.strip()

        if '==' in condition:
            left, right = map(str.strip, condition.split('=='))
            if left == right:
                result = self.execute(command_if, line_number)
                if result is not None:
                    print(result)
        elif '>>' in condition:
            left, right = map(str.strip, condition.split('>>'))
            if float(left) > float(right):
                result = self.execute(command_if, line_number)
                if result is not None:
                    print(result)
        elif '<<' in condition:
            left, right = map(str.strip, condition.split('<<'))
            if float(left) < float(right):
                result = self.execute(command_if, line_number)
                if result is not None:
                    print(result)
        elif '>>==' in condition:
            left, right = map(str.strip, condition.split('>>=='))
            if float(left) >= float(right):
                result = self.execute(command_if, line_number)
                if result is not None:
                    print(result)
        elif '<<==' in condition:
            left, right = map(str.strip, condition.split('<<=='))
            if float(left) <= float(right):
                result = self.execute(command_if, line_number)
                if result is not None:
                    print(result)
        elif '!=' in condition:
            left, right = map(str.strip, condition.split('!='))
            if left!= right:
                result = self.execute(command_if, line_number)
                if result is not None:
                    print(result)
        elif condition:
            if isinstance(condition, bool):
                result = self.execute(command_if, line_number)
                if result is not None:
                    print(result)
        else:

            raise SyntaxError(f"Invalid condition syntax in line {line_number}:\n>= {command_if}")

        return None

    def set_block(self, name_block, command_block=''):
        if name_block is not None and command_block is not None:
            self.block_store.add_block(name_block, command_block)
        else:
            raise CommandError("Invalid block command.")

    def processing_block(self, command_block, line_number):
        name_block = self.name_block
        block = self.block_store.get_block(name_block)
        if block is not None:
            self.block_store.add_command_block(name_block, command_block)
        else:
            raise CommandError("Unknown block - {name}".format(name=name_block))


    def import_mod(self, name):
        if name is not None:
            mod = get_mod(name)
            if mod:
                self.mods[name] = mod
            else:
                raise CommandError("Unknown module - {name}".format(name=name))
        else:
            raise CommandError("Invalid module name")

    def update(self, *args):
        text = ' '.join(args)
        variable, upd_value = text.split(':=')
        variable = variable.strip()
        var = self.variable_store.get_variable(variable)
        if var:
            var.value = upd_value.strip()
        else:
            raise VariableError("Unknown variable - {name}".format(name=var))

    def terminal(self, command):
        return os.system(command)


    def math(self, *args, line_number):
        if len(args) < 5 or args[1] != ':=':
            if args[1] == '=' or args[1] == ':' or args[1] == '=:':
                raise CommandError(f"Incorrect syntax in line {line_number}. Expected: `math [{{variable}}] := [{{expression}}]`.\nReceived: `math {' '.join(args)}`\nPerhaps you meant: `math {args[0]} := {' '.join(args[2:])}`.")

        result_var = args[0][2:-2].strip()
        expression = ' '.join(args[2:])

        def replace_variable(match):
            var_name = match.group(1).strip()
            variable = self.variable_store.get_variable(var_name)
            if variable is not None:
                return str(variable.value)
            else:
                raise VariableError(f"The variable '{var_name}' in line {line_number} was not found.")

        expression = re.sub(r'\[\{(.*?)\}\]', replace_variable, expression)

        try:
            allowed_functions = {
                'sin': math.sin,
                'cos': math.cos,
                'tan': math.tan,
                'sqrt': math.sqrt,
                'log': math.log,
                'log10': math.log10,
                'pow': pow,
            }

            for func in allowed_functions:
                expression = re.sub(rf'\b{func}\s*\((.*?)\)', lambda m: str(allowed_functions[func](*map(float, m.group(1).split(',')))), expression)

            result = eval(expression)
        except Exception as e:
            raise CommandError(f"Error when calculating the expression in line {line_number}:\n{e}")

        if isinstance(result, int):
            self.set_variable("int", f"{result_var} := {result}")
        else:
            self.set_variable("float", f"{result_var} := {result}")

        return None

    def obj(self, *args, line_number):
        if len(args) < 4 or args[1] != ':=':
            if args[1] == '=' or args[1] == ':' or args[1] == '=:':
                raise CommandError(f"Incorrect syntax in line {line_number}. Expected: `obj [{{variable}}] := varible_dict_or_list key_or_id`.\nReceived: `obj {' '.join(args)}`\nPerhaps you meant: `obj {args[0]} := {' '.join(args[2:])}`.")

        result_var = args[0][2:-2].strip()
        variable_name = args[2].strip()
        obj = args[3].strip()
        obj = re.sub(r'\[\{(.*?)\}\]', lambda match: str(self.variable_store.get_variable(match.group(1).strip()).value), obj)
        obj = re.sub(r'\[\{\s*', '[{', obj)
        obj = re.sub(r'\s*\}\]', '}]', obj)

        variable = self.variable_store.get_variable(variable_name)
        if variable is None:
            raise VariableError(f"Variable '{variable_name}' not found.")

        if isinstance(variable, ListVariable):
            index = int(obj)
            if index < 0 or index >= len(variable.value):
                raise IndexError(f"Index {index} out of range for list variable '{variable_name}'.")
            value = variable.value[index]
            self.set_variable("str", f"{result_var} := {value}")
        elif isinstance(variable, DictVariable):
            key = obj.strip()
            if key not in variable.value:
                raise KeyError(f"Key '{key}' not found in dict variable '{variable_name}'.")
            value = variable.value[key]
            self.set_variable("str", f"{result_var} := {value}")
        else:
            raise VariableError(f"Variable '{variable_name}' is not a list or dict.")

        return None



    def execute(self, command, line_number):
        parts = command.split()
        if parts[0] == "mods":
            if parts[1] == "init":
                initialize_moduls()
        elif parts[0] == "set":
            if parts[1] == "output":
                var_type = parts[2]
                name_value = ' '.join(parts[3:])
                return self.set_variable(var_type, name_value, output=True)
            elif len(parts) >= 4:
                var_type = parts[1]
                name_value = ' '.join(parts[2:])
                return self.set_variable(var_type, name_value)
        elif parts[0] == "block":
            try:
                arrow_index = parts.index(':')
            except ValueError:
                raise CommandError(f"Invalid block command in line {line_number}. Did you forget to add `:`?")
            self.is_block = True
            name_block = self.name_block = parts[1]
            return self.set_block(name_block)
        elif parts[0] == "input":
            if parts[1] == "->":
                var_type = parts[2]
                name = parts[3]
                prompt = ' '.join(parts[4:])
                return self.input_variable(var_type, name, prompt)
            else:
                raise CommandError("Invalid input command. Did you forget to add `->`?")
        elif parts[0] == 'upd':
            return self.update(*parts[1:])
        elif parts[0] == "delete":
            if parts[1] == "output":
                name = parts[2]
                return self.delete_variable(name, output=True)
            elif len(parts) == 2:
                name = parts[1]
                return self.delete_variable(name)
        elif parts[0] == "output":
            return self.output(*parts[1:])
        elif parts[0] == "<-#->":
            return
        elif parts[0] == "if":
            try:
                arrow_index = parts.index(':')
            except ValueError:
                raise CommandError(f"Invalid if command in line {line_number}. Did you forget to add `:`?")
            condition = ' '.join(parts[1:arrow_index])
            self.is_if = True
            return self.set_if(condition, line_number)
        elif parts[0] == ">":
            if self.is_if:
                command_if = ' '.join(parts[1:])
                return self.processing_if(command_if, line_number)
            elif self.is_block:
                command_block = ' '.join(parts[1:])
                return self.processing_block(command_block, line_number)
            else:
                raise CommandError("Invalid command. Did you forget to add if or block?")
        elif parts[0] == "endif":
            self.is_if = False
            return None
        elif parts[0] == "endblock":
            self.is_block = False
            return None
        elif parts[0] == "run":
            name_block = parts[1]
            block = self.block_store.get_block(name_block)
            if block:
                block = block[5:].split('\|/')
                for command in block:
                    result = self.execute(command, line_number)
                    if result:
                        print(result)
                return None
            else:
                raise CommandError(f"Block '{name_block}' not found.")
        elif parts[0] == "import":
            name = parts[1]
            return self.import_mod(name)
        elif parts[0] == "from":
            file = parts[1]
            if parts[2] == "import_block":
                block = parts[3]
                self.from_import_block(file, block)
            elif parts[2] == "import_var":
                variable = parts[3]
                self.from_import_variable(file, variable)
            else:
                raise CommandError(f"Invalid import command - `{' '.join(parts)}` in line {line_number}.\nExpected: `from path/to/file/.dark` import_block/import_var block/var.\nReceived: `{' '.join(parts)}`")
        elif parts[0] == "terminal":
            command = ' '.join(parts[1:])
            command = re.sub(r'\[\{(.*?)\}\]', lambda match: str(self.variable_store.get_variable(match.group(1).strip()).value), command)
            command = re.sub(r'\[\{\s*', '[{', command)
            command = re.sub(r'\s*\}\]', '}]', command)
            return self.terminal(command)
        elif parts[0] == "math":
            return self.math(*parts[1:], line_number=line_number)
        elif parts[0] == "obj":
            return self.obj(*parts[1:], line_number=line_number)
        else:
            mod = self.mods.get(parts[0], None)
            if mod is not None:
                args = []
                for arg in parts[1:]:
                    if arg.startswith('[{') and arg.endswith('}]'):
                        var_name = arg[2:-2]
                        variable = self.variable_store.get_variable(var_name)
                        if variable:
                            args.append(variable.value)
                        else:
                            block = self.block_store.get_block(var_name)
                            if block:
                                block = block.split('\|/')
                                for command in block:
                                    args.append(command)
                            else:
                                args.append(arg)
                    else:
                        args.append(arg)
                return mod(*args)
            else:
                raise VariableError(f"Unknown line {line_number}:\n`{' '.join(parts)}`.")
