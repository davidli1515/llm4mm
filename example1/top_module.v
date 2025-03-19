
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

    wire [7:0] out;
    wire [3:0] next_state;
    wire m1_out;
    wire [254:0] in;
    wire m1_in;
    wire [3:0] state;
    module0 u_module0 (
        .in(in),
        .out(out)
    );

    module1 u_module1 (
        .m1_in(m1_in),
        .state(state),
        .next_state(next_state),
        .m1_out(m1_out)
    );


    wire [7:0] arbiter_in_out0_in1; 
    wire [4:0] arbiter_out_out0_in1; 

    width_arbitrator #(
        .IN_WIDTH(8),
        .OUT_WIDTH(5)
    ) arbitrator_out0_in1 (
        .clk(clk),
        .rst_n(rst_n),
        .valid_in(valid_in),
        .arbiter_in(arbiter_in_out0_in1),
        .valid_out(valid_out),
        .arbiter_out(arbiter_out_out0_in1),
        .ready_in(ready_in)
    );    

        assign out = arbiter_in_out0_in1[7:0];
    assign state = arbiter_out_out0_in1[3:0];
    assign m1_in = arbiter_out_out0_in1; 

    wire [3:0] arbiter_in_out1_in0; 
    wire [254:0] arbiter_out_out1_in0; 

    width_arbitrator #(
        .IN_WIDTH(4),
        .OUT_WIDTH(255)
    ) arbitrator_out1_in0 (
        .clk(clk),
        .rst_n(rst_n),
        .valid_in(valid_in),
        .arbiter_in(arbiter_in_out1_in0),
        .valid_out(valid_out),
        .arbiter_out(arbiter_out_out1_in0),
        .ready_in(ready_in)
    );    

        assign next_state = arbiter_in_out1_in0[3:0];
    assign in = arbiter_out_out1_in0[254:0];








endmodule

    