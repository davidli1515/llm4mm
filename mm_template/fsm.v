
module fsm (
    input  logic clk,
    
    input  logic [7:0] fsm_in_q,
    output logic fsm_out_a,
    output logic fsm_out_b,
    output logic fsm_out_c,
    output logic fsm_out_d,
    input  logic rst
);
    typedef enum reg [1:0] {IDLE, WORK, DONE} state_t;
    state_t state, next_state;


    always @(posedge clk or posedge rst) begin
        if (rst)
            state <= IDLE;
        else
            state <= next_state;
    end


    always_comb begin
        case (state)
            IDLE: next_state = WORK;
            WORK: next_state = DONE;
            DONE: next_state = IDLE;
            default: next_state = IDLE;
        endcase
    end


    always_comb begin
        case (state)
            IDLE: begin
                fsm_out_a = 0;
                fsm_out_b = 0;
                fsm_out_c = 0;
                fsm_out_d = 0;
            end
            WORK: begin
                fsm_out_a = {fsm_in_q[7]};
                fsm_out_b = {fsm_in_q[6]};
                fsm_out_c = {fsm_in_q[5]};
                fsm_out_d = {fsm_in_q[4]};
            end
            DONE: begin
                fsm_out_a = 0;
                fsm_out_b = 0;
                fsm_out_c = 0;
                fsm_out_d = 0;
            end
            default: begin
                fsm_out_a = 0;
                fsm_out_b = 0;
                fsm_out_c = 0;
                fsm_out_d = 0;
            end
        endcase
    end


endmodule

    