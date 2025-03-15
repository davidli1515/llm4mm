
module top_module (
    input  logic clk,
    input  logic rst
);

    wire out_sop;
    wire out_pos;

    wire [7:0] arbiter_out_d;
    wire arbiter_out_reset;

    wire [7:0] q;

    wire fsm_out_a;
    wire fsm_out_b;
    wire fsm_out_c;
    wire fsm_out_d;

    module0 u_module0 (
        .a(fsm_out_a),
        .b(fsm_out_b),
        .c(fsm_out_c),
        .d(fsm_out_d),
        .out_sop(out_sop),
        .out_pos(out_pos)
    );


    arbiter u_arbiter (
        .clk(clk),
        .rst(rst),
        .out_sop(out_sop),
        .out_pos(out_pos),
        .arbiter_out_d(arbiter_out_d),
        .arbiter_out_reset(arbiter_out_reset)
    );


    module1 u_module1 (
        .clk(clk),
        .d(arbiter_out_d),
        .reset(arbiter_out_reset),
        .q(q)
    );


    fsm u_fsm (
        .clk(clk),
        .rst(rst),
        .fsm_in_q(q),
        .fsm_out_a(fsm_out_a),
        .fsm_out_b(fsm_out_b),
        .fsm_out_c(fsm_out_c),
        .fsm_out_d(fsm_out_d)
    );


endmodule

    