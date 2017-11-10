module popcount8(in1,in2,out);
input [7:0]in1;
input [7:0]in2;
output [3:0]out;

assign out = (in1[0]^in2[0]) + (in1[1]^in2[1]) + (in1[2]^in2[2]) + (in1[3]^in2[3]) + (in1[4]^in2[4]) + (in1[5]^in2[5]) + (in1[6]^in2[6]) + (in1[7]^in2[7]);

endmodule
