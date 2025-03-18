
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

    wire out_sop;
    wire out_pos;
    wire [7:0] q;
    wire a;
    wire b;
    wire c;
    wire d;
    wire [7:0] m1_d;
    wire reset;
    module0 u_module0 (
        .a(a),
        .b(b),
        .c(c),
        .d(d),
        .out_sop(out_sop),
        .out_pos(out_pos)
    );

    module1 u_module1 (
        .clk(clk),
        .m1_d(m1_d),
        .reset(reset),
        .q(q)
    );


    wire arbiter_in_out0_in1;    wire [8:0] arbiter_out_out0_in1; 

    width_arbitrator #(
        .IN_WIDTH(1),
        .OUT_WIDTH(9)
    ) arbitrator_out0_in1 (
        .clk(clk),
        .rst_n(rst_n),
        .valid_in(valid_in),
        .arbiter_in(arbiter_in_out0_in1),
        .valid_out(valid_out),
        .arbiter_out(arbiter_out_out0_in1),
        .ready_in(ready_in)
    );    

        assign out_pos = arbiter_in_out0_in1; 
    assign reset = arbiter_out_out0_in1; 
    assign m1_d = arbiter_out_out0_in1[7:1];

    wire [7:0] arbiter_in_out1_in0; 
    wire [3:0] arbiter_out_out1_in0; 

    width_arbitrator #(
        .IN_WIDTH(8),
        .OUT_WIDTH(4)
    ) arbitrator_out1_in0 (
        .clk(clk),
        .rst_n(rst_n),
        .valid_in(valid_in),
        .arbiter_in(arbiter_in_out1_in0),
        .valid_out(valid_out),
        .arbiter_out(arbiter_out_out1_in0),
        .ready_in(ready_in)
    );    

        assign q = arbiter_in_out1_in0[7:0];
    assign c = arbiter_out_out1_in0; 
    assign d = arbiter_out_out1_in0; 
    assign a = arbiter_out_out1_in0; 
    assign b = arbiter_out_out1_in0; 


    wire fsm_in_out0_arbiter;    wire fsm_out_out0_arbiter;
    fsm_generated #(
        .IN_WIDTH(1),
        .OUT_WIDTH(4)
) fsm_out0_arbiter (
    .clk(clk),
    .rst_n(rst_n),
    .in_signal(fsm_in_out0_arbiter),  
    .out_signal(fsm_out_out0_arbiter)  
);

    assign out_sop = fsm_in_out0_arbiter; 
    assign fsm_out_arbiter_port_out0_in1 = fsm_out_out0_arbiter[3:0];

    wire [3:0] arbiter_in_fsm_in1; 
    wire arbiter_out_fsm_in1;
    width_arbitrator #(
        .IN_WIDTH(4),
        .OUT_WIDTH(1)
    ) arbitrator_fsm_in1 (
        .clk(clk),
        .rst_n(rst_n),
        .valid_in(valid_in),
        .arbiter_in(arbiter_in_fsm_in1),
        .valid_out(valid_out),
        .arbiter_out(arbiter_out_fsm_in1),
        .ready_in(ready_in)
    );    

        assign fsm_out_arbiter_port_out0_in1 = arbiter_in_fsm_in1[3:0];





endmodule

    