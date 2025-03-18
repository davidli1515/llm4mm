module width_arbitrator #(
    parameter IN_WIDTH  = 10,    // Width of the input port
    parameter OUT_WIDTH = 2     // Width of the output port
)(
    input  wire                  clk,      // Clock
    input  wire                  rst_n,    // Active-low reset
    input  wire                  valid_in, // Input data valid
    input  wire [IN_WIDTH-1:0]   arbiter_in,  // Input data
    output wire                  valid_out,// Output data valid
    output wire [OUT_WIDTH-1:0]  arbiter_out, // Output data
    output wire                  ready_in  // Ready to accept new input
);

    // Internal signals and registers
    generate
        // Case 1: Input width is larger than output width (Parallel to Serial)
        if (IN_WIDTH > OUT_WIDTH) begin : p2s
            localparam COUNTER_WIDTH = $clog2(IN_WIDTH / OUT_WIDTH + (IN_WIDTH % OUT_WIDTH != 0));
            localparam NUM_TRANSFERS = (IN_WIDTH + OUT_WIDTH - 1) / OUT_WIDTH; // Ceiling division
            
            reg [IN_WIDTH-1:0]      data_buffer;
            reg [COUNTER_WIDTH-1:0] counter;
            reg                     output_valid;
            reg                     input_ready;
            
            // Control logic
            always @(posedge clk or negedge rst_n) begin
                if (!rst_n) begin
                    counter <= 0;
                    output_valid <= 0;
                    input_ready <= 1;
                    data_buffer <= 0;
                end else begin
                    if (input_ready && valid_in) begin
                        // Capture new input data
                        data_buffer <= arbiter_in;
                        counter <= 0;
                        output_valid <= 1;
                        input_ready <= 0;
                    end else if (output_valid) begin
                        if (counter == NUM_TRANSFERS - 1) begin
                            // Last transfer completed
                            counter <= 0;
                            output_valid <= 0;
                            input_ready <= 1;
                        end else begin
                            // Shift to next chunk
                            counter <= counter + 1;
                        end
                    end
                end
            end
            
            // Output assignment
            assign arbiter_out = data_buffer[OUT_WIDTH * (counter + 1) - 1 -: OUT_WIDTH];
            assign valid_out = output_valid;
            assign ready_in = input_ready;
        end
        
        // Case 2: Input width is smaller than output width (Serial to Parallel)
        else if (IN_WIDTH < OUT_WIDTH) begin : s2p
            localparam COUNTER_WIDTH = $clog2(OUT_WIDTH / IN_WIDTH + (OUT_WIDTH % IN_WIDTH != 0));
            localparam NUM_TRANSFERS = (OUT_WIDTH + IN_WIDTH - 1) / IN_WIDTH; // Ceiling division
            
            reg [OUT_WIDTH-1:0]     data_buffer;
            reg [COUNTER_WIDTH-1:0] counter;
            reg                     output_valid;
            reg                     input_ready;
            
            // Control logic
            always @(posedge clk or negedge rst_n) begin
                if (!rst_n) begin
                    counter <= 0;
                    output_valid <= 0;
                    input_ready <= 1;
                    data_buffer <= 0;
                end else begin
                    if (input_ready && valid_in) begin
                        // Accumulate input data
                        data_buffer[(counter+1)*IN_WIDTH-1 -: IN_WIDTH] <= arbiter_in;
                        
                        if (counter == NUM_TRANSFERS - 1) begin
                            // All chunks received
                            counter <= 0;
                            output_valid <= 1;
                            input_ready <= 0;
                        end else begin
                            // Wait for more chunks
                            counter <= counter + 1;
                        end
                    end else if (output_valid) begin
                        // Output data transferred
                        output_valid <= 0;
                        input_ready <= 1;
                    end
                end
            end
            
            // Output assignment
            assign arbiter_out = data_buffer;
            assign valid_out = output_valid;
            assign ready_in = input_ready;
        end
        
        // Case 3: Input width equals output width (Pass-through)
        else begin : pass
            assign arbiter_out = arbiter_in;
            assign valid_out = valid_in;
            assign ready_in = 1'b1;
        end
    endgenerate

endmodule
