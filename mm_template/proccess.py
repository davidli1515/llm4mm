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

    module1_ports = "\n".join([
        f"    input  logic {port['name']}," if port['width'] == 1 else f"    input  logic [{port['width']-1}:0] arbiter_in_{port['name']},"
        for port in module0_outputs if port['name'] != 'clk'
    ])

    arbiter_outputs = "\n".join([
        f"    output logic arbiter_out_{port['name']}," if port['width'] == 1 else f"    output logic [{port['width']-1}:0] arbiter_out_{port['name']},"
        for port in module1_inputs if port['name'] != 'clk'
    ]) 

    arbiter_logic = "    always_comb begin\n"
    offset = 0
    for port in module1_inputs:
        if port['name'] != 'clk':
            arbiter_logic += f"        arbiter_out_{port['name']} = arbiter_out[{offset + port['width'] - 1}:{offset}];\n" if port['width'] > 1 else \
                             f"        arbiter_out_{port['name']} = arbiter_out[{offset}];\n"
            offset += port['width']
    arbiter_logic += "    end\n"

    state_logic = """    logic [1:0] state;
    always_ff @(posedge clk or posedge rst) begin
        if (rst)
            state <= 0;
        else
            state <= state + 1'b1;
    end
"""

    arbiter_assignment = "    always_ff @(posedge clk or posedge rst) begin\n"
    arbiter_assignment += "        if (rst)\n"
    arbiter_assignment += "            arbiter_out <= 0;\n"
    arbiter_assignment += "        else begin\n"
    arbiter_assignment += "            case (state)\n"
    
    state_offset = 0
    for port in module0_outputs:
        arbiter_assignment += f"                {state_offset}: arbiter_out <= {port['name']};\n"
        state_offset += 1

    arbiter_assignment += """                default: arbiter_out <= 0;
            endcase
        end
    end
"""
   
    arbiter_out_def = f"    logic [{offset-1}:0] arbiter_out;"

    verilog_code = f"""
module arbiter (
    input  logic clk,
{module1_ports}
{arbiter_outputs}
    input  logic rst
);

{arbiter_out_def}

{state_logic}

{arbiter_assignment}

{arbiter_logic}

endmodule

    """

    return verilog_code
    
def generate_verilog_fsm(module1_outputs, module0_inputs):
    
    def extract_bits(bit_str):
        return list(map(int, bit_str.replace('[', '').replace(']', '').split(':')))

    def bit_match(module1_outputs, module0_inputs) -> str:
        input_ports = module1_outputs
        output_ports = module0_inputs

        input_bits_list = []
        for port in input_ports:
            for bit in range(port['width'] - 1, -1, -1):
                input_bits_list.append(f"fsm_in_{port['name']}[{bit}]")

        matched_bits = []
        current_input_bit = 0

        for port in output_ports:
            port_bits = port['width']
            port_name = f"fsm_out_{port['name']}"
            assignments = []
            for bit in range(port_bits - 1, -1, -1):
                if current_input_bit < len(input_bits_list):
                    assignments.append(input_bits_list[current_input_bit])
                    current_input_bit += 1
                else:
                    assignments.append("1'b0")
            matched_bits.append(f"                {port_name} = {{{', '.join(assignments)}}}")

        return ';\n'.join(matched_bits) + ';\n'

    print(bit_match(module1_outputs, module0_inputs))

    fsm_inputs = "\n".join([
        f"    input  logic fsm_in_{port['name']}," if port['width'] == 1 else f"    input  logic [{port['width']-1}:0] fsm_in_{port['name']},"
        for port in module1_outputs
    ])

    fsm_outputs = "\n".join([
        f"    output logic fsm_out_{port['name']}," if port['width'] == 1 else f"    output logic [{port['width']-1}:0] fsm_out_{port['name']},"
        for port in module0_inputs
    ])

    state_definitions = """    typedef enum reg [1:0] {IDLE, WORK, DONE} state_t;
    state_t state, next_state;
"""

    state_transition = """    always @(posedge clk or posedge rst) begin
        if (rst)
            state <= IDLE;
        else
            state <= next_state;
    end
"""

    next_state_logic = """    always_comb begin
        case (state)
            IDLE: next_state = WORK;
            WORK: next_state = DONE;
            DONE: next_state = IDLE;
            default: next_state = IDLE;
        endcase
    end
"""

    fsm_logic = "    always_comb begin\n"
    fsm_logic += "        case (state)\n"
    fsm_logic += "            IDLE: begin\n"
    for port in module0_inputs:
        fsm_logic += f"                fsm_out_{port['name']} = 0;\n"
    fsm_logic += "            end\n"
    fsm_logic += "            WORK: begin\n"
    offset = 0

    # for port in module0_inputs:
    #     fsm_logic += f"                fsm_out_{port['name']} = fsm_in_{module1_outputs[offset % len(module1_outputs)]['name']};\n"
    #     offset += 1
    fsm_logic += bit_match(module1_outputs, module0_inputs)
    
    fsm_logic += "            end\n"
    fsm_logic += "            DONE: begin\n"
   
   
    for port in module0_inputs:
        fsm_logic += f"                fsm_out_{port['name']} = 0;\n"
    fsm_logic += "            end\n"
    fsm_logic += """            default: begin
"""

    for port in module0_inputs:
        fsm_logic += f"                fsm_out_{port['name']} = 0;\n"
    fsm_logic += "            end\n"
    fsm_logic += "        endcase\n"
    fsm_logic += "    end\n"

    verilog_code = f"""
module fsm (
    input  logic clk,
    
{fsm_inputs}
{fsm_outputs}
    input  logic rst
);
{state_definitions}

{state_transition}

{next_state_logic}

{fsm_logic}

endmodule

    """

    return verilog_code




def generate_verilog_top(module0_outputs, module1_inputs, module1_outputs, module0_inputs):

    arbiter_width = sum(port['width'] for port in module1_inputs)
    fsm_width = sum(port['width'] for port in module0_inputs)
    
    module0_inputs_original = module0_inputs
    module1_inputs_original = module1_inputs
    module0_inputs = [port for port in module0_inputs if port['name'] != 'clk']
    module1_inputs = [port for port in module1_inputs if port['name'] != 'clk']

    module0_output_ports = "\n".join([
        f"    wire {port['name']};" if port['width'] == 1 else f"    wire [{port['width']-1}:0] {port['name']};"
        for port in module0_outputs
    ])

    # module0_input_ports = "\n".join([
    #     f"    wire {port['name']};" if port['width'] == 1 else f"    wire [{port['width']-1}:0] {port['name']};"
    #     for port in module0_inputs
    # ])

    # module1_input_ports = "\n".join([
    #     f"    wire {port['name']};" if port['width'] == 1 else f"    wire [{port['width']-1}:0] {port['name']};"
    #     for port in module1_inputs
    # ])
    
    module1_output_ports = "\n".join([
        f"    wire {port['name']};" if port['width'] == 1 else f"    wire [{port['width']-1}:0] {port['name']};"
        for port in module1_outputs
    ])

    arbiter_signals = "\n".join([
        f"    wire arbiter_out_{port['name']};" if port['width'] == 1 else f"    wire [{port['width']-1}:0] arbiter_out_{port['name']};"
        for port in module1_inputs
    ])
    fsm_signals = "\n".join([
        f"    wire fsm_out_{port['name']};" if port['width'] == 1 else f"    wire [{port['width']-1}:0] fsm_out_{port['name']};"
        for port in module0_inputs
    ])

    module0_inst = "    module0 u_module0 (\n"
    module0_inst += ",\n".join([
        f"        .{port['name']}(fsm_out_{port['name']})" for port in module0_inputs
    ])

    module0_inst += ",\n"

    module0_inst += ",\n".join([
        f"        .{port['name']}({port['name']})" for port in module0_outputs
    ])

    module0_inst += "\n    );\n"

    arbiter_inst = "    arbiter u_arbiter (\n"
    arbiter_inst += "        .clk(clk),\n        .rst(rst),\n"
    arbiter_inst += ",\n".join([
        f"        .{port['name']}({port['name']})" for port in module0_outputs
    ])
    arbiter_inst += ",\n"
    arbiter_inst += ",\n".join([
        f"        .arbiter_out_{port['name']}(arbiter_out_{port['name']})" for port in module1_inputs
    ])
    arbiter_inst += "\n    );\n"

    module1_inst = "    module1 u_module1 (\n"
    # module1_inst += ",\n".join([
    #     f"        .{port['name']}(arbiter_out_{port['name']})" for port in module1_inputs
    # ])
    
    # module1_inst += ",\n"
    for port in module1_inputs_original:
        if (port['name'] == 'clk'):
             module1_inst += f"        .clk(clk),\n" 
        else:
            module1_inst += f"        .{port['name']}(arbiter_out_{port['name']}),\n"

    module1_inst += ",\n".join([
        f"        .{port['name']}({port['name']})" for port in module1_outputs
    ])
    module1_inst += "\n    );\n"

    fsm_inst = "    fsm u_fsm (\n"
    fsm_inst += "        .clk(clk),\n        .rst(rst),\n"
    fsm_inst += ",\n".join([
        f"        .fsm_in_{port['name']}({port['name']})" for port in module1_outputs
    ])
    fsm_inst += ",\n"
    fsm_inst += ",\n".join([
        f"        .fsm_out_{port['name']}(fsm_out_{port['name']})" for port in module0_inputs
    ])
    fsm_inst += "\n    );\n"

    verilog_code = f"""
module top_module (
    input  logic clk,
    input  logic rst
);

{module0_output_ports}

{arbiter_signals}

{module1_output_ports}

{fsm_signals}

{module0_inst}

{arbiter_inst}

{module1_inst}

{fsm_inst}

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
    verilog_file_path0 = '/home/weihang/attentionDSE/MAGE/verilog-eval/dataset_code-complete-iccad2023/Prob070_ece241_2013_q2_ref.sv'
    verilog_file_path1 = '/home/weihang/attentionDSE/MAGE/verilog-eval/dataset_code-complete-iccad2023/Prob046_dff8p_ref.sv'

    ports_info0 = extract_ports_from_file(verilog_file_path0)
    ports_info1 = extract_ports_from_file(verilog_file_path1)

    in_port0, out_port0 = split_ports(ports_info0)
    in_port1, out_port1 = split_ports(ports_info1)
    
    # out_port1 --> arbiter --> in_port2
    arbiter_output = generate_verilog_arbiter(out_port0, in_port1)
    file_path = '/home/weihang/attentionDSE/MAGE/multi-module/mm_template/arbiter.v'
    write_helper(arbiter_output, file_path)
    # print(arbiter_output)

    # out_port2 --> FSM --> in_port1
    fsm_output = generate_verilog_fsm(out_port1, in_port0)
    file_path = '/home/weihang/attentionDSE/MAGE/multi-module/mm_template/fsm.v'
    write_helper(fsm_output, file_path)
    # print(fsm_output)

    # verilog_output = generate_verilog_top(module0_outputs, module1_inputs, module1_outputs, module0_inputs)
    topmodule_output = generate_verilog_top(out_port0, in_port1, out_port1, in_port0)
    file_path = '/home/weihang/attentionDSE/MAGE/multi-module/mm_template/top_module.v'
    write_helper(topmodule_output, file_path)
    print(topmodule_output)
    # for port in ports_info1:
    #     print(port)

    # for port in ports_info2:
    #     print(port)

    # **生成 Verilog 代码**
    # verilog_output = generate_verilog_arbiter(module1_outputs, module2_inputs)
    # print(verilog_output)
