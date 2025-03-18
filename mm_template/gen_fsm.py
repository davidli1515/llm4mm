import numpy as np
import random

def generate_directed_graph(n):
    np.random.seed(42)  
    graph = np.zeros((n, n), dtype=int)

    # Ensure the graph is connected (create a random traversal path)
    nodes = list(range(n))
    random.shuffle(nodes)
    for i in range(n - 1):
        graph[nodes[i], nodes[i + 1]] = 1 

    # Add extra random edges, allowing cycles
    for _ in range(n * 2):  
        src, dst = random.randint(0, n - 1), random.randint(0, n - 1)
        if src != dst:  
            graph[src, dst] = 1

    return graph

def generate_verilog_state_enum(n):
    """ Generate Verilog FSM state definition """
    num_bits = (n - 1).bit_length()  # Calculate required state bits
    state_enum = f"    typedef enum logic [{num_bits - 1}:0] {{\n"
    state_enum += ",\n".join([f"        STATE_{i+1} = {num_bits}'d{i}" for i in range(n)])
    state_enum += "\n    } state_t;\n"
    return state_enum


# def random_4bit():
#     return f"4'b{random.randint(0, 15):04b}"

# def generate_random_condition():
#     bit1 = random.randint(0, 10)
#     bit2 = random.randint(0, 10)
#     condition = f"((in_signal[{bit1} % IN_WIDTH] & in_signal[{bit2} % IN_WIDTH]) ? {random_4bit()} : {random_4bit()}) {random.choice(['<', '>'])} {random_4bit()}"
#     return condition

# def generate_random_output():
#     bit1 = random.randint(0, 10)
#     bit2 = random.randint(0, 10)
#     output_expr = f"((in_signal[{bit1} % IN_WIDTH] & in_signal[{bit2} % IN_WIDTH]) ? {random_4bit()} : {random_4bit()}) & {{OUT_WIDTH{{1'b1}}}} "
#     return output_expr

def generate_random_condition():
    """ Generate a random state transition condition based on IN_WIDTH parameter """
    bit1 = random.randint(0, 10)
    bit2 = random.randint(0, 10)
    # operator = random.choice(["&", "&&", "~|"])
    operator = random.choice(["&&"])
    comparator = random.choice([">", "<", "=="])
    condition = f"((in_signal[{bit1} % IN_WIDTH] {operator} in_signal[{bit2} % IN_WIDTH]) {comparator} (IN_WIDTH / 2))"
    return condition

def generate_random_output():
    """ Generate a random output signal logic based on IN_WIDTH and OUT_WIDTH parameters """
    bit1 = random.randint(0, 10)
    bit2 = random.randint(0, 10)
    # operator = random.choice(["+", "-", "&", "|", "~|"])
    operator = random.choice(["&&"])
    output_expr = f"(in_signal[{bit1} % IN_WIDTH] {operator} in_signal[{bit2} % IN_WIDTH]) & ((1 << OUT_WIDTH) - 1)"
    return output_expr

def generate_verilog_fsm(n):
    IN_WIDTH = 8  # Modify input width as needed
    OUT_WIDTH = 4  # Modify output width as needed
    graph = generate_directed_graph(n)  # Generate state transition graph
    state_enum = generate_verilog_state_enum(n)  # Generate state definition

    verilog_code = f"""
module fsm_generated #(
    parameter IN_WIDTH = {IN_WIDTH},
    parameter OUT_WIDTH = {OUT_WIDTH}
) (
    input  wire clk,
    input  wire rst_n,
    input  wire [IN_WIDTH-1:0] in_signal,  // Input signal
    output reg  [OUT_WIDTH-1:0] out_signal  // Output signal
);

""" + state_enum + """
    state_t state, next_state;

    // **First Section: State Register (Synchronous Logic)**
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n)
            state <= STATE_1;  // Reset to initial state
        else
            state <= next_state;
    end

    // **Second Section: State Transition (Combinational Logic)**
    always @(*) begin
        case (state)
"""

    for i in range(n):
        verilog_code += f"            STATE_{i+1}: begin\n"
        transitions = [f"STATE_{j+1}" for j in range(n) if graph[i][j] == 1]
        if len(transitions) >= 2:
            condition = generate_random_condition()
            verilog_code += f"                if ({condition}) next_state = {transitions[0]};\n"
            verilog_code += f"                else next_state = {transitions[1]};\n"
        elif len(transitions) == 1:
            verilog_code += f"                next_state = {transitions[0]};\n"
        else:
            verilog_code += f"                next_state = STATE_1;\n"
        verilog_code += f"            end\n"

    verilog_code += """
            default: next_state = STATE_1;
        endcase
    end

    // **Third Section: Output Logic (Combinational Logic)**
    always @(*) begin
        case (state)
"""

    for i in range(n):
        output_expr = generate_random_output()
        verilog_code += f"            STATE_{i+1}: out_signal = {output_expr};\n"

    verilog_code += """
            default: out_signal = 0;
        endcase
    end

endmodule
"""
    return verilog_code

# Set the number of states
total_states = 5  # Modify as needed
verilog_fsm_code = generate_verilog_fsm(total_states)

# Save to file
with open("fsm_generated.v", "w") as f:
    f.write(verilog_fsm_code)

print("Verilog FSM code has been generated and saved to fsm_generated.v")

