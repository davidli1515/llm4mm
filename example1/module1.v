
module module1 (
  input m1_in,
  input [3:0] state,
  output reg [3:0] next_state,
  output m1_out
);

  parameter A=0, B=1, C=2, D=3;

  assign next_state[A] = (state[A] | state[C]) & ~m1_in;
  assign next_state[B] = (state[A] | state[B] | state[D]) & m1_in;
  assign next_state[C] = (state[B] | state[D]) & ~m1_in;
  assign next_state[D] = state[C] & m1_in;

  assign m1_out = (state[D]);

endmodule

