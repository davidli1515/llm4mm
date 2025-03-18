import re
import sys
import numpy as np
from typing import List, Tuple
from port_map import group_ports
from gen_fsm import generate_verilog_fsm
from gen_arbiter import generate_verilog_arbiter
import random

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

def singal_assign(module_port: List[dict], singal_name: str) -> str:
    output_str = ''
    left_value, right_value = 0, 0
    for signal in module_port:
        left_value += int(signal['width']) - 1
        if signal['name'] != 'clk':
            if int(signal['width']) == 1:
                output_str += f"    assign {signal['name']} = {singal_name}; \n"
            else: 
                output_str += f"    assign {signal['name']} = {singal_name}[{left_value}:{right_value}];\n"
            right_value = left_value + 1
        
    return output_str

def generate_arbiter_top(arbiter_in_port, arbiter_out_port, arbiter_index: str) -> str:
    
    in_width = sum(int(port['width']) for port in arbiter_in_port)
    out_width = sum(int(port['width']) for port in arbiter_out_port)
    arbiter_in = f'arbiter_in_{arbiter_index}'
    arbiter_out = f'arbiter_out_{arbiter_index}'

    arbiter_instantiate = f"""
    width_arbitrator #(
        .IN_WIDTH({in_width}),
        .OUT_WIDTH({out_width})
    ) arbitrator_{arbiter_index} (
        .clk(clk),
        .rst_n(rst_n),
        .valid_in(valid_in),
        .arbiter_in({arbiter_in}),
        .valid_out(valid_out),
        .arbiter_out({arbiter_out}),
        .ready_in(ready_in)
    );    

    """

    wire_arbiter = f"    wire {arbiter_in};" if in_width == 1 else f"    wire [{in_width-1}:0] {arbiter_in}; \n"
    wire_arbiter += f"    wire {arbiter_out};" if out_width == 1 else f"    wire [{out_width-1}:0] {arbiter_out}; \n"

    arbiter_singal_assign = singal_assign(arbiter_in_port, f'arbiter_in_{arbiter_index}') + singal_assign(arbiter_out_port, f'arbiter_out_{arbiter_index}')
    
    return wire_arbiter+ arbiter_instantiate + arbiter_singal_assign 

def generate_fsm_top(fsm_in_port, fsm_out_port, fsm_index: str) -> str:

    in_width = sum(int(port['width']) for port in fsm_in_port)
    out_width = sum(int(port['width']) for port in fsm_out_port)
    fsm_in = f'fsm_in_{fsm_index}'
    fsm_out = f'fsm_out_{fsm_index}'

    fsm_instantiate = f"""
    fsm_generated #(
        .IN_WIDTH({in_width}),
        .OUT_WIDTH({out_width})
) fsm_{fsm_index} (
    .clk(clk),
    .rst_n(rst_n),
    .in_signal(fsm_in_{fsm_index}),  
    .out_signal(fsm_out_{fsm_index})  
);

"""
    fsm_singal_assign = singal_assign(fsm_in_port, f'fsm_in_{fsm_index}') + singal_assign(fsm_out_port, f'fsm_out_{fsm_index}')
    wire_fsm =   f"    wire {fsm_in};" if in_width == 1 else f"    wire [{in_width-1}:0] {fsm_in}; \n"
    wire_fsm +=   f"    wire {fsm_out};" if in_width == 1 else f"    wire [{in_width-1}:0] {fsm_out}; \n"

    return wire_fsm+ fsm_instantiate + fsm_singal_assign

def generate_verilog_top(module0_outputs, module1_inputs, module1_outputs, module0_inputs):

    in_port1_arbiter, in_port1_fsm, out_port0_arbiter, out_port0_fsm = group_ports(module1_inputs, module0_outputs)
    in_port0_arbiter, in_port0_fsm, out_port1_arbiter, out_port1_fsm = group_ports(module0_inputs, module1_outputs)
    # print(in_port0_arbiter, in_port0_fsm, out_port1_arbiter, out_port1_fsm)
    # out0_arbiter_width = sum(port['width'] for port in out_port0_arbiter)
    # in1_arbiter_width = sum(port['width'] for port in in_port1_arbiter)
    
    # out0 --> arbiter --> in1
    arbiter_top_out0_in1 = generate_arbiter_top(out_port0_arbiter, in_port1_arbiter, 'out0_in1')
    # out1 --> arbiter --> in0
    arbiter_top_out1_in0 = generate_arbiter_top(out_port1_arbiter, in_port0_arbiter, 'out1_in0')
    
    # out0 --> fsm --> arbiter --> in1 
    np.random.seed(41) 
    fsm_out_width_out0_arbiter = random.randint(1, 8)
    fsm_out_arbiter_port_out0_in1 = [{'name': 'fsm_out_arbiter_port_out0_in1', 'width': str(fsm_out_width_out0_arbiter)}]
    
    if out_port0_fsm:
        fsm_top_out0_arbiter = generate_fsm_top(out_port0_fsm, fsm_out_arbiter_port_out0_in1, 'out0_arbiter')
    else:
        fsm_top_out0_arbiter = ''
    
    print(in_port1_fsm)
    if in_port1_fsm:
        arbiter_top_fsm_in1 = generate_arbiter_top(fsm_out_arbiter_port_out0_in1, in_port1_fsm, 'fsm_in1')
    else:
        arbiter_top_fsm_in1 = ''

    # out1 --> fsm --> arbiter --> in0
    np.random.seed(42) 
    fsm_out_width_out1_arbiter = random.randint(1, 8)
    fsm_out_arbiter_port_out1_in0 = [{'name': 'fsm_out_arbiter_port_out1_in0', 'width': str(fsm_out_width_out1_arbiter)}]
    
    if out_port1_fsm:
        fsm_top_out1_arbiter = generate_fsm_top(out_port1_fsm, fsm_out_arbiter_port_out1_in0, 'out1_arbiter')
    else:
        fsm_top_out1_arbiter = ''
    
    if in_port0_fsm:
        arbiter_top_fsm_in0 = generate_arbiter_top(fsm_out_arbiter_port_out1_in0, in_port0_fsm, 'fsm_in0')
    else:
        arbiter_top_fsm_in0 = ''

    module0_output_ports = "\n".join([
        f"    wire {port['name']};" if port['width'] == 1 else f"    wire [{port['width']-1}:0] {port['name']};"
        for port in module0_outputs
    ])

    module1_output_ports = "\n".join([
        f"    wire {port['name']};" if port['width'] == 1 else f"    wire [{port['width']-1}:0] {port['name']};"
        for port in module1_outputs
    ])

    module0_input_ports = "\n".join([
        f"    wire {port['name']};" if port['width'] == 1 else f"    wire [{port['width']-1}:0] {port['name']};"
        for port in module0_inputs if port['name'] != 'clk'
    ])

    module1_input_ports = "\n".join([
        f"    wire {port['name']};" if port['width'] == 1 else f"    wire [{port['width']-1}:0] {port['name']};"
        for port in module1_inputs if port['name'] != 'clk'
    ])

    module0_top = "    module0 u_module0 (\n"
    module0_top += ",\n".join([
        f"        .{port['name']}({port['name']})" for port in module0_inputs
    ])
    module0_top += ",\n"
    module0_top += ",\n".join([
        f"        .{port['name']}({port['name']})" for port in module0_outputs
    ])
    module0_top += "\n    );\n"

    module1_top = "    module1 u_module1 (\n"
    module1_top += ",\n".join([
        f"        .{port['name']}({port['name']})" for port in module1_inputs
    ])
    module1_top += ",\n"
    module1_top += ",\n".join([
        f"        .{port['name']}({port['name']})" for port in module1_outputs
    ])
    module1_top += "\n    );\n"
    

    verilog_code = f"""
module top_module (
    input  logic clk,
    input  logic rst
);

wire valid_in;
assign valid_in = 1'b1; 

wire ready_in;
assign ready_in = 1'b1; 

wire rst_n;
assign rst_n = 1'b0; 

{module0_output_ports}
{module1_output_ports}
{module0_input_ports}
{module1_input_ports}
{module0_top}
{module1_top}

{arbiter_top_out0_in1}
{arbiter_top_out1_in0}

{fsm_top_out0_arbiter}
{arbiter_top_fsm_in1}

{fsm_top_out1_arbiter}
{arbiter_top_fsm_in0}

endmodule

    """

    return verilog_code

def split_ports(ports_info: List) -> Tuple[List, List]:
    in_port, out_port = [], []
    for port in ports_info:
        if port["direction"] == 'input':
            in_port.append({"width": port["width"], "name": port["name"]})
        elif port["direction"] == 'output':
            out_port.append({"width": port["width"], "name": port["name"]})
    return in_port, out_port

def write_helper(verilog_code: str, file_path: str):
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(verilog_code)

if __name__ == "__main__":
    verilog_file_path0 = '/home/weihang/attentionDSE/MAGE/multi-module/mm_template/module0.v'
    verilog_file_path1 = '/home/weihang/attentionDSE/MAGE/multi-module/mm_template/module1.v'

    ports_info0 = extract_ports_from_file(verilog_file_path0)
    ports_info1 = extract_ports_from_file(verilog_file_path1)

    # singal data structure
    # in_port0: [{'name': 'in_port0_singal0', 'width': '2'},
    #            {'name': 'in_port0_singal1', 'width': '4'},
    #            {'name': 'in_port0_singal2', 'width': '5'}]

    in_port0, out_port0 = split_ports(ports_info0)
    in_port1, out_port1 = split_ports(ports_info1)

    # out_port1 --> arbiter --> in_port2
    generate_verilog_arbiter(out_port0, in_port1)
    # file_path = '/home/weihang/attentionDSE/MAGE/multi-module/mm_template/arbiter.v'
    # write_helper(arbiter_output, file_path)
    # print(arbiter_output)

    fsm_verilog = generate_verilog_fsm(4)
    file_path = '/home/weihang/attentionDSE/MAGE/multi-module/mm_template/fsm_generated.v'
    write_helper(fsm_verilog, file_path)
    # print(fsm_output)

    # verilog_output = generate_verilog_top(module0_outputs, module1_inputs, module1_outputs, module0_inputs)
    topmodule_output = generate_verilog_top(out_port0, in_port1, out_port1, in_port0)
    file_path = '/home/weihang/attentionDSE/MAGE/multi-module/mm_template/top_module.v'
    write_helper(topmodule_output, file_path)
    print(topmodule_output)