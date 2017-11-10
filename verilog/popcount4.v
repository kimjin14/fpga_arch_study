module popcount4(in1,in2,out);
input [3:0]in1;
input [3:0]in2;
output [2:0]out;

assign out = (in1[0]^in2[0]) + (in1[1]^in2[1]) + (in1[2]^in2[2]) + (in1[3]^in2[3]);

endmodule
