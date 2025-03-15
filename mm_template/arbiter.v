
module arbiter (
    input  logic clk,
    input  logic out_sop,
    input  logic out_pos,
    output logic [7:0] arbiter_out_d,
    output logic arbiter_out_reset,
    input  logic rst
);

    logic [8:0] arbiter_out;

    logic [1:0] state;
    always_ff @(posedge clk or posedge rst) begin
        if (rst)
            state <= 0;
        else
            state <= state + 1'b1;
    end


    always_ff @(posedge clk or posedge rst) begin
        if (rst)
            arbiter_out <= 0;
        else begin
            case (state)
                0: arbiter_out <= out_sop;
                1: arbiter_out <= out_pos;
                default: arbiter_out <= 0;
            endcase
        end
    end


    always_comb begin
        arbiter_out_d = arbiter_out[7:0];
        arbiter_out_reset = arbiter_out[8];
    end


endmodule

    