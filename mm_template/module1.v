
module module1 (
  input clk,
  input [7:0] m1_d,
  input reset,
  output reg [7:0] q
);

  always @(negedge clk)
    if (reset)
      q <= 8'h34;
    else
      q <= m1_d;

endmodule

