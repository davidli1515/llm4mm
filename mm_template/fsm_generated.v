
module fsm_generated #(
    parameter IN_WIDTH = 8,
    parameter OUT_WIDTH = 4
) (
    input  wire clk,
    input  wire rst_n,
    input  wire [IN_WIDTH-1:0] in_signal,  // Input signal
    output reg  [OUT_WIDTH-1:0] out_signal  // Output signal
);

    typedef enum logic [1:0] {
        STATE_1 = 2'd0,
        STATE_2 = 2'd1,
        STATE_3 = 2'd2,
        STATE_4 = 2'd3
    } state_t;

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
            STATE_1: begin
                next_state = STATE_3;
            end
            STATE_2: begin
                next_state = STATE_3;
            end
            STATE_3: begin
                if (((in_signal[6 % IN_WIDTH] && in_signal[4 % IN_WIDTH]) == (IN_WIDTH / 2))) next_state = STATE_1;
                else next_state = STATE_2;
            end
            STATE_4: begin
                next_state = STATE_2;
            end

            default: next_state = STATE_1;
        endcase
    end

    // **Third Section: Output Logic (Combinational Logic)**
    always @(*) begin
        case (state)
            STATE_1: out_signal = (in_signal[0 % IN_WIDTH] && in_signal[2 % IN_WIDTH]) & ((1 << OUT_WIDTH) - 1);
            STATE_2: out_signal = (in_signal[5 % IN_WIDTH] && in_signal[6 % IN_WIDTH]) & ((1 << OUT_WIDTH) - 1);
            STATE_3: out_signal = (in_signal[8 % IN_WIDTH] && in_signal[3 % IN_WIDTH]) & ((1 << OUT_WIDTH) - 1);
            STATE_4: out_signal = (in_signal[7 % IN_WIDTH] && in_signal[8 % IN_WIDTH]) & ((1 << OUT_WIDTH) - 1);

            default: out_signal = 0;
        endcase
    end

endmodule
