import re
import sys
from typing import List, Tuple


def extract_ports_from_file(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        verilog_code = f.read()

    pattern = r'\b(input|output|inout)\s+(?:wire|reg)?\s*(?:\[(\d+):(\d+)\])?\s*(\w+)'
    matches = re.findall(pattern, verilog_code)

    ports = []
    for direction, msb, lsb, name in matches:
        width = abs(int(msb) - int(lsb)) + 1 if msb and lsb else 1
        ports.append({"direction": direction, "width": width, "name": name})

    return ports

def generate_verilog_arbiter(module0_outputs, module1_inputs):
    total_out_width = sum(port['width'] for port in module0_outputs)
    total_in_width = sum(port['width'] for port in module1_inputs)
    arbiter_template = '/home/weihang/attentionDSE/MAGE/multi-module/mm_template/arbiter_template.v'
    arbiter_real = '/home/weihang/attentionDSE/MAGE/multi-module/mm_template/width_arbitrator.v'
    
    def generate_from_template(arbiter_template, arbiter_real, total_in_width, total_out_width):
        with open(arbiter_template, 'r') as file:
                lines = file.readlines()
    
        updated_lines = []
        for line in lines:
            line = re.sub(r'(parameter\s+IN_WIDTH\s*=)\s*\d+', rf'\1 {total_in_width}', line)
            line = re.sub(r'(parameter\s+OUT_WIDTH\s*=)\s*\d+', rf'\1 {total_out_width}', line)
            updated_lines.append(line)
    
        with open(arbiter_real, 'w') as file:
            file.writelines(updated_lines)

    generate_from_template(arbiter_template, arbiter_real, total_in_width, total_out_width)
