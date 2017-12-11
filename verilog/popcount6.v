module popcount6(in1,in2,out);

parameter I_WIDTH = 6;
parameter O_WIDTH = 3;

input [I_WIDTH-1:0]in1;
input [I_WIDTH-1:0]in2;
output [O_WIDTH-1:0]out;

assign out = (in1[0]^in2[0]) + (in1[1]^in2[1]) + (in1[2]^in2[2]) + (in1[3]^in2[3]) + (in1[4]^in2[4]) + (in1[5]^in2[5]);

endmodule

