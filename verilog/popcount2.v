module popcount2(in1,in2,out);
input [1:0]in1;
input [1:0]in2;
output [1:0]out;

assign out = (in1[0]^in2[0]) + (in1[1]^in2[1]);

endmodule
